from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from random import randrange
import pandas as pd
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

    def end_session(self):
        """Close out browser."""
        self.driver.quit()

    def user_login(self, username, password):
        self.driver.delete_all_cookies()
        try:
            self.driver.get('https://www.youtube.com/')
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="avatar-btn"]'))).click()
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/div[1]/yt-multi-page-menu-section-renderer[1]/div[2]/ytd-compact-link-renderer[4]/a/tp-yt-paper-item/div[2]/yt-formatted-string[1]'))).click()
        except:
            pass

        self.driver.get('https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en&ec=65620')

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.ID, 'identifierId'))).send_keys(username)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="identifierNext"]'))).click()


        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@type="password"]'))).send_keys(password)


        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="passwordNext"]/div/button'))).click()
        time.sleep(5)

    def run(self, username, password,categoryList,length_interval):
        """Build data frame from list of queries and sanitize results"""
        self.user_login(username=username, password=password)

        self.watch_from_homepage(categoryList,length_interval)

        self.click_sidebar(3,length_interval)
        print("EXECUTED SUCCESSFULLY")
        return

    def log_out(self):
        self.driver.get('https://www.youtube.com/')
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="avatar-btn"]'))).click()
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/div[1]/yt-multi-page-menu-section-renderer[1]/div[2]/ytd-compact-link-renderer[4]/a/tp-yt-paper-item/div[2]/yt-formatted-string[1]'))).click()


        
    
    def watch_from_homepage(self,categoryList,length_interval):
        self.driver.get('https://www.youtube.com/')
        time.sleep(3)

        ids = self.getIds("id","video-title-link")
        
        url = "https://www.googleapis.com/youtube/v3/videos?part=snippet&id={id}&key={api_key}"
        for id in ids:
            data = requests.get(url.format(id=id, api_key=DEVELOPER_KEY)).json()
            
            if data['items']:
                if int(data['items'][0]['snippet']['categoryId']) in categoryList:
                    duration = self.getDuration(id)
                    if duration>0 and duration<=1800:
                        self.watch_video(id,self.getRandomLengthPercentage(length_interval))
                        break
                    



    def watch_video(self,id,percentage):
        #get video total length by visiting the url
        duration = self.getDuration(id)
        
        #calculate the percentage of the length
        watch_time = duration * percentage/100
        
        self.driver.get('https://www.youtube.com/watch?v='+id)
        time.sleep(2)

        #how to deal with ads??
        try:
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable(By.CLASS_NAME,'ytp-ad-skip-button-container'))
        except:
            pass
        
        #return when the time is up
        time.sleep(watch_time)
        
        return

    
    def click_sidebar(self, number, length_interval):
        watched = 0
        time.sleep(2)
        
        #while hitting a certain number
        while watched<number:
            ids = self.getIds(By.CSS_SELECTOR,".yt-simple-endpoint.style-scope.ytd-compact-video-renderer")
            self.watch_video(self.getRandomChoice(ids),self.getRandomLengthPercentage(length_interval))
            watched+=1
        #continue to randomly select video from sidebar
        return
    
    
    def  getRandomChoice(self,list):
        choice = randrange(len(list))
        while self.getDuration(list[choice])<=0 or self.getDuration(list[choice])>1800:
            choice = randrange(len(list))
        return list[choice]

    def getRandomLengthPercentage(self,list):
        return randrange(list[0],list[1])   
    
    def getDuration(self,id):
        url = 'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={id}&key={api_key}'
        data = requests.get(url.format(id=id,api_key=DEVELOPER_KEY)).json()
        print(data)
        seconds = 0
        if data['items']:
            duration = data['items'][0]['contentDetails']['duration']
            day = re.findall('(\d+)D',duration)
            hour = re.findall('(\d+)H',duration)
            minute = re.findall('(\d+)M',duration)
            second = re.findall('(\d+)S',duration)
            if day:
                seconds += int(day[0])*24*60*60
            if hour:
                seconds += int(hour[0])*60*60
            if minute:
                seconds += int(minute[0])*60
            if second:
                seconds += int(second[0])
            
            print(seconds)
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

    def getIds(self,by,identifier_name):
        links = self.driver.find_elements(by,identifier_name)
        ids = []
        ids += [link.get_attribute('href') for link in links]
        ids = [id.strip('https://www.youtube.com/watch?v=') for id in filter(None,ids)]
        return ids
    
if __name__ == '__main__':
    iterator_ = YoutubeIterator()
    username = 'prometheuslabai00001@gmail.com'
    password = 'nanababa123'
    categoryList = [24,10]
    length_interval = [50,80]
    iterator_.run(username, password,categoryList,length_interval)
