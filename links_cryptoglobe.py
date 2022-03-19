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

def get_links(browser):
    page = browser.page_source
    soup = BeautifulSoup(page, "html.parser")

    list = soup.find_all("div", class_="item-news ng-scope")

    n = 0
    with open("output/cryptoglobe/links", "w") as file:
        for div in list:
            heading = div.find("h3")
            link = heading.find("a", class_="ng-binding")
            if link['href'] != '':
                file.write(link['href'] + "\n")
                n += 1
    print("{} links have been saved.".format(n))

def scroll_down(browser):
    last_height = browser.execute_script("return document.body.scrollHeight")

    page = 1
    print("Page {} loaded.".format(page))

    while True:
        if page % 10 == 0:
            get_links(browser)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        page += 1
        print("Page {} loaded.".format(page))
        time.sleep(2)

        new_height = browser.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height
    
    return browser

def load_browser(url, save_page=False, load_from_memory=False):
    if load_from_memory == True:
        with open('output/tmp_loaded_page', 'r') as f:
            return f.read()

    chrome_options = Options() 
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)

    if save_page == True:
        loaded_html = browser.page_source
        with open('output/tmp_loaded_page', 'w') as f:
            f.write(loaded_html)

    return browser

if __name__ == "__main__":
    url = "https://www.cryptocompare.com/news/list/latest/?feeds=cryptoglobe"

    browser = load_browser(url)
    browser = scroll_down(browser)
    get_links(browser)