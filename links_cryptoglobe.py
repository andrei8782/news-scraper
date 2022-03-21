from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import time
from random import randrange
import requests
import sys

class LinkScraper:
    def __init__(self, url):
        chrome_options = Options() 
        # chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.get(url)



    def get_links(self, out_file):
        page = self.browser.page_source
        soup = BeautifulSoup(page, "html.parser")

        list = soup.find_all("div", class_="item-news ng-scope")

        n = 0
        # out_file = "output/cryptoglobe/sample_links"
        # tmp_file = "output/cryptoglobe/tmp_links"
        with open(out_file, "w") as file:
            for div in list:
                heading = div.find("h3")
                link = heading.find("a", class_="ng-binding")['href']
                if link == '':
                    continue
                file.write(link + "\n")
                n += 1
        print("{} links have been saved.".format(n))

    def scroll_down(self, out_file):
        last_height = self.browser.execute_script("return document.body.scrollHeight")

        page = 1
        print("Page {} loaded.".format(page))

        while True:
            if page % 5 == 0:
                self.get_links(out_file)
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            page += 1
            print("Page {} loaded.".format(page))
            time.sleep(2)

            new_height = self.browser.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height
        
        return self.browser

if __name__ == "__main__":
    url = "https://www.cryptocompare.com/news/list/latest/?feeds=cryptoglobe"
    link_scraper = LinkScraper(url)
    link_scraper.scroll_down(out_file="output/cryptoglobe/tmp_links")
    link_scraper.get_links(out_file="output/cryptoglobe/tmp_links")