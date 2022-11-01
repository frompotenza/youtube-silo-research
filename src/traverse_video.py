from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from random import randrange
import time
import requests
import re

DRIVER_PATH = r"PUT YOUR DRIVER PATH"
DEVELOPER_KEY = "PUT YOUR DEVELOPER KEY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


class YoutubeIterator:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-web-security")
        options.add_argument(
            '--user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.61 Safari/537.36"')
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--lang=en-US")
        self.driver = uc.Chrome(executable_path=DRIVER_PATH,
                                options=options, version_main=106, use_subprocess=True)
        self.search_start = 'https://www.youtube.com/results?search_query='

    def user_login(self, username, password):
        self.driver.delete_all_cookies()

        # log out first if the previous session was not logged out
        try:
            self.driver.get('https://www.youtube.com/')
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="avatar-btn"]'))).click()
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/div[1]/yt-multi-page-menu-section-renderer[1]/div[2]/ytd-compact-link-renderer[4]/a/tp-yt-paper-item/div[2]/yt-formatted-string[1]'))).click()
        except:
            pass

        # go to the log in page for YouTube Google accounts
        self.driver.get('https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en&ec=65620')

        # try with directly enter the username
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, 'identifierId'))).send_keys(username)

        # Google saves other accounts that are previously logged out during the session, so in that case we can't log in directly
        # so we click to log in with a different account
        except:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'BHzsHc'))).click()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, 'identifierId'))).send_keys(username)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="identifierNext"]'))).click()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@type="password"]'))).send_keys(password)

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="passwordNext"]/div/button'))).click()

    def watch_from_homepage(self, categoryList, percentage_interval, length_interval):
        '''
        Start watching video from YouTube homepage. Will check if the video is in
        the category that we are interested in and if the duration of the video is within
        the range that we specified. As soon as we find a video that filfills the criteria,
        the program will start watching the video and go through the process of clicking sidebar.
        '''

        self.driver.get('https://www.youtube.com/')

        # get all the ids of the video recommended on the home page
        ids = self.get_ids("id", "video-title-link")

        # url for visiting a page
        url = "https://www.googleapis.com/youtube/v3/videos?part=snippet&id={id}&key={api_key}"

        for id in ids:
            # get metadata of a video
            data = requests.get(url.format(
                id=id, api_key=DEVELOPER_KEY)).json()

            # sometimes the id doesn't point to a video but a livestream session or a playlist,
            # in that case 'items' will be empty, so we need to check if it's a valid video
            if data['items']:
                if int(data['items'][0]['snippet']['categoryId']) in categoryList:
                    duration = self.get_duration(id)
                    if duration > length_interval[0] and duration <= length_interval[1]:
                        # watch the video if passed the checks for a random length within the range
                        self.watch_video(
                            id, self.get_random_length_percentage(percentage_interval))
                        break

    def watch_video(self, id, percentage):
        '''
        Watch a video for a certain duration. The duration is obtained by calculating with 
        the percentage specified since users usually don't watch the video till the very end.
        Will go back to the program where this function is called after getting to percentage
        of the total length of the video.
        '''
        # get video total length by visiting the url
        duration = self.get_duration(id)

        # calculate the percentage of the length
        watch_time = duration * percentage/100
        self.driver.get('https://www.youtube.com/watch?v='+id)
        time.sleep(2)

        # skip adds when possible
        try:
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable(By.CLASS_NAME, 'ytp-ad-skip-button-container'))
        except:
            pass

        # watch until time is up
        time.sleep(watch_time)

    def click_sidebar(self, number, percentage_interval, length_interval):
        '''Watch videos from sidebar until number of videos specified is reached.'''
        watched = 0

        # keep watching until enough
        while watched < number:
            #get a list of the ids of the videos on the sidebar
            ids = self.get_ids(
                By.CSS_SELECTOR, ".yt-simple-endpoint.style-scope.ytd-compact-video-renderer")
            #randomly choose one to watch from teh list
            self.watch_video(self.get_random_choice(
                ids, length_interval), self.get_random_length_percentage(percentage_interval))
            watched += 1

    def get_random_choice(self, list, length_interval):
        '''Helper function taht choose one video(that filfills the video length criteria) by random from a list of videos.'''
        choice = randrange(len(list))
        while self.get_duration(list[choice]) <= length_interval[0] or self.get_duration(list[choice]) > length_interval[1]:
            choice = randrange(len(list))
        return list[choice]

    def get_random_length_percentage(self, list):
        '''
        Helper function that returns an interger from the interval given. For example, if we want
        to stop watching a video between 50% to 80% of its total length, this function takes [50,80]
        and will return an integer between that interval.
        '''
        return randrange(list[0], list[1])

    def get_duration(self, id):
        url = 'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={id}&key={api_key}'
        data = requests.get(url.format(id=id, api_key=DEVELOPER_KEY)).json()
        seconds = 0
        if data['items']:
            duration = data['items'][0]['contentDetails']['duration']
            day = re.findall('(\d+)D', duration)
            hour = re.findall('(\d+)H', duration)
            minute = re.findall('(\d+)M', duration)
            second = re.findall('(\d+)S', duration)
            if day:
                seconds += int(day[0])*24*60*60
            if hour:
                seconds += int(hour[0])*60*60
            if minute:
                seconds += int(minute[0])*60
            if second:
                seconds += int(second[0])
            return seconds
        return -1

    def getCategoryId(self):
        url = 'https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode=CA&key={api_key}'
        categoryId = requests.get(url.format(api_key=DEVELOPER_KEY)).json()
        short_categoryId = {}

        if categoryId['items']:
            for i in categoryId['items']:
                short_categoryId[i['snippet']['title']] = i['id']
        else:
            print('CategoryId EMPTY! API Request Failed')
        return short_categoryId

    def get_ids(self, by, identifier_name):
        '''A helper function to collect '''
        links = self.driver.find_elements(by, identifier_name)
        ids = []
        ids += [link.get_attribute('href') for link in links]
        ids = [id.strip('https://www.youtube.com/watch?v=')
               for id in filter(None, ids)]
        return ids

    def log_out(self):
        '''Log out of the current account.'''
        # go to YouTube homepage
        self.driver.get('https://www.youtube.com/')

        # click on the profile photo in the up right corner
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="avatar-btn"]'))).click()

        # click logout
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/div[1]/yt-multi-page-menu-section-renderer[1]/div[2]/ytd-compact-link-renderer[4]/a/tp-yt-paper-item/div[2]/yt-formatted-string[1]'))).click()

    def end_session(self):
        '''Terminate the driver.'''
        self.driver.quit()

    def run(self, usernames, password, categoryList, percentage_interval, length_interval, num_sidebar):
        '''
        Main function that orchestrate the whole process of traversing through videos.
        Iterate through the list of usernames in order and make each one of the accounts to watch videos according to
        the speficiations.
        '''
        for i in range(len(usernames)):
            self.user_login(username=usernames[i], password=password[i])

            self.watch_from_homepage(
                categoryList[i], percentage_interval[i], length_interval[i])

            self.click_sidebar(
                num_sidebar[i], percentage_interval[i], length_interval[i])
            self.log_out()

        print("EXECUTED SUCCESSFULLY")


if __name__ == '__main__':
    iterator_ = YoutubeIterator()

    ######################MODIFY HERE TO USE THE PROGRAM#######################
    usernames = ['USERNAME1', 'USERNAME2']
    password = ['PASSWORD1', 'PASSWORD2']
    categoryList = [[24, 10, 22, 27, 23], [24, 23, 28, 20, 10]]
    percentage_interval = [[50, 80], [50, 80]]
    length_interval = [[0, 18000], [0, 18000]]
    num_sidebar = [2, 2]
    ###########################################################################

    iterator_.run(usernames, password, categoryList,
                  percentage_interval, length_interval, num_sidebar)
