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
        self.search_start = 'https://www.youtube.com/results?search_query='
        self.query = []
        self.titles = []
        self.hrefs = []
        self.users = []
        self.userlist = []
        self.clean_titles = []
        self.df = pd.DataFrame()

    def search(self, search_term):
        full_path = self.search_start+search_term
        self.driver.get(full_path)

        while True:
            scroll_height = 2000
            document_height_before = self.driver.execute_script(
                "return document.documentElement.scrollHeight")
            self.driver.execute_script(
                f"window.scrollTo(0, {document_height_before + scroll_height});")
            time.sleep(1.5)
            document_height_after = self.driver.execute_script(
                "return document.documentElement.scrollHeight")

            if document_height_after == document_height_before:
                break

        time.sleep(3)

    def get_titles(self):
        results = self.driver.find_elements("id", 'video-title')
        self.titles = self.titles + [result.text for result in results]
        self.hrefs = self.hrefs + \
            [result.get_attribute('href') for result in results]
        return len(results)

    def clean_(self, title):
        title = re.sub(r'[^A-Za-z ]+', '', title)
        return title.lower()

    def end_session(self):
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

        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, 'identifierId'))).send_keys(username)
        except:
            WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CLASS_NAME,'BHzsHc'))).click()
            time.sleep(3)            
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, 'identifierId'))).send_keys(username)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="identifierNext"]'))).click()

        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@type="password"]'))).send_keys(password)

        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="passwordNext"]/div/button'))).click()
        time.sleep(5)

    def get_result(self, queries, username, password):
        for username in self.userlist:
            self.user_login(username=username, password=password)
            for query in queries:
                self.search(query)
                num_of_results = self.get_titles()
                self.users = self.users + ([username]*num_of_results)
                self.query = self.query + ([query]*num_of_results)
            try:
                self.log_out()
            except:
                pass
        self.df['User'] = username
        self.df['Query'] = self.query
        self.df['Titles'] = self.titles
        self.df['URL'] = self.hrefs
        self.df['Clean_Titles'] = self.df['Titles'].apply(
            lambda x: self.clean_(x))
        self.end_session()
        return self.df

    def log_out(self):
        self.driver.get('https://www.youtube.com/')
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="avatar-btn"]'))).click()
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/div[1]/yt-multi-page-menu-section-renderer[1]/div[2]/ytd-compact-link-renderer[4]/a/tp-yt-paper-item/div[2]/yt-formatted-string[1]'))).click()


if __name__ == '__main__':
    scraper = YoutubeScraper()
    ####### need to replace with your own value ########
    username = ['USERNAME1']
    password = 'PASSWORD'
    # a list of keywords that we want to scrape the search results for
    words = ['python tutorial', 'best camera review']
    ####################################################
    result = scraper.get_result(words, username, password)
    result.to_csv("output.csv")
