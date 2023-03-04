import datetime
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import pandas as pd
import re
import time

DRIVER_PATH = r"PUT YOUR DRIVER PATH"

class YoutubeScraper:
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
        self.home = 'https://www.youtube.com/'
        self.query = []
        self.titles = []
        self.hrefs = []
        self.users = []
        self.dates = []
        self.clean_titles = []
        self.userlist = []
        self.password = []
        self.df = pd.DataFrame()

    def _get_titles(self):
        '''Append video titles and its hyperlink to the result list'''
        results = self.driver.find_elements("id", 'video-title-link')
        ctr = 0
        titles = []
        hrefs = []
        for result in results:
            if result.get_attribute('title'):
                titles.append(result.get_attribute('title'))
                hrefs.append(result.get_attribute('href'))
                ctr+=1
        self.titles = self.titles + titles
        self.hrefs = self.hrefs + hrefs
        return ctr

    def _clean_(self, title):
        '''Helper function to clean the title results.'''
        title = re.sub(r'[^A-Za-z ]+', '', title)
        return title.lower()

    def user_login(self, username, password):
        '''Log into the YouTube account using the input username and password.'''
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
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, 'identifierId'))).send_keys(username)
        except:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'BHzsHc'))).click()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, 'identifierId'))).send_keys(username)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="identifierNext"]'))).click()

        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@type="password"]'))).send_keys(password)
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="passwordNext"]/div/button'))).click()


    def get_result(self):
        '''The main program to scrape results using all the accounts.'''
        for i in range(len(self.userlist)):
            print("SCRAPING FOR USER: ", self.userlist[i])
            self.user_login(
                username=self.userlist[i], password=self.password[i])
            self.driver.get(self.home)
            time.sleep(3)            
            num_of_results = self._get_titles()
            self.users = self.users + ([self.userlist[i]]*num_of_results)
            self.dates = self.dates + ([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]*num_of_results)
            try:
                self.log_out()
            except:
                pass
            
        self.df['User'] = self.users
        self.df['Titles'] = self.titles
        self.df['URL'] = self.hrefs
        self.df['Clean_Titles'] = self.df['Titles'].apply(
            lambda x: self._clean_(x))

        self.end_session()
        return self.df

    def log_out(self):
        '''Log out from the current account.'''
        self.driver.get('https://www.youtube.com/')
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="avatar-btn"]'))).click()
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/div[1]/yt-multi-page-menu-section-renderer[1]/div[2]/ytd-compact-link-renderer[4]/a/tp-yt-paper-item/div[2]/yt-formatted-string[1]'))).click()
    
    def end_session(self):
        '''Terminate driver session.'''
        self.driver.quit()

if __name__ == '__main__':
    scraper = YoutubeScraper()
    ######################MODIFY HERE TO USE THE PROGRAM#######################
    scraper.userlist = ['USERNAME1']
    scraper.password = ['PASSWORD']
    output_path = "test_scrape.csv"
    ###########################################################################

    result = scraper.get_result()
    result.to_csv(output_path, mode='a', header=not os.path.exists(output_path))
