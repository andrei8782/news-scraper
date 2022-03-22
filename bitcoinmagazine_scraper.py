from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import time
from random import randrange
from link_scraper import LinkScraper

class BitcoinmagazineScraper(LinkScraper):
    def __init__(self, article_limit=None, ignore_overlap=False) -> None:
        super().__init__(website="bitcoinmagazine", article_limit=article_limit, ignore_overlap=ignore_overlap)
        self.base_link = "https://bitcoinmagazine.com"
        self.reached_endpage = False

        accept_cookies_XPATH = '/html/body/div/div[2]/div[3]/button'
        consent_iframe_XPATH = '//*[@id="sp_message_iframe_446779"]'
        WebDriverWait(self.browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, consent_iframe_XPATH)))
        WebDriverWait(self.browser, 15).until(EC.element_to_be_clickable((By.XPATH, accept_cookies_XPATH))).click()
        time.sleep(3)

        close_ad_button_XPATH = '//*[@id="lyra-wrapper"]/div/div[4]/phoenix-ad[2]/div/div[2]/div'
        # close_ad = WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.XPATH, close_ad_button_XPATH)))
        # close_ad.click()

        self.load_button_XPATH = '//*[@id="main-content"]/section[2]/phoenix-hub/div/phoenix-footer-loader/button'

    def render_page(self):
        try:
            # rand_delay = randrange(10)
            # time.sleep(rand_delay)

            ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
            load_more = WebDriverWait(self.browser, 1000, ignored_exceptions=ignored_exceptions)\
                .until(EC.element_to_be_clickable((By.XPATH, self.load_button_XPATH)))
            self.browser.execute_script('arguments[0].click()', load_more)

        except Exception as e:
            print(e)
            self.reached_endpage = True
            
    def parse_links(self):
        links = []
        time.sleep(3)
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        list = soup.find("phoenix-hub", class_="m-card-group--container")
        for article in list.find_all("phoenix-super-link"):
            article_link = article['href']
            if article_link == '':
                continue
            else:
                links.append(self.base_link + article_link)
        return links


    def reached_end_of_webpage(self):
        return self.reached_endpage
