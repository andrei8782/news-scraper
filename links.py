from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
import time
from random import randrange

URL = "https://bitcoinmagazine.com/articles"

chrome_options = Options() 
chrome_options.add_experimental_option("detach", True)
browser = webdriver.Chrome(options=chrome_options)
browser.get(URL)


accept_cookies_XPATH = '/html/body/div/div[2]/div[3]/button'
consent_iframe_XPATH = '//*[@id="sp_message_iframe_446779"]'
WebDriverWait(browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, consent_iframe_XPATH)))
WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.XPATH, accept_cookies_XPATH))).click()

close_ad_button_XPATH = '//*[@id="lyra-wrapper"]/div/div[4]/phoenix-ad[2]/div/div[2]/div'
close_ad = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, close_ad_button_XPATH)))
close_ad.click()

load_button_XPATH = '//*[@id="main-content"]/section[2]/phoenix-hub/div/phoenix-footer-loader/button'

def write_to_file(browser, pages):
    print("Loaded " + str(pages) + " pages.\n")
    time.sleep(3)
    loaded_html = browser.page_source
    soup = BeautifulSoup(loaded_html, "html.parser")

    list = soup.find("phoenix-hub", class_="m-card-group--container")

    num = 0
    with open("output/tmp.txt", "w") as file:
        for article in list.find_all("phoenix-super-link"):
            file.write(article['href'])
            file.write('\n')
            num += 1

    print("Loaded " + str(num) + " articles.\n")

pages = 1
while True:
    try:
        if (pages > 1):
            clock_end = time.time()
            print("Loaded in {:.2f} seconds.\n".format(clock_end - clock_start))

        if pages % 10 == 0:
            write_to_file(browser, pages)

        print("Page " + str(pages + 1) + " loading...\n")
        
        clock_start = time.time()
        rand_delay = randrange(20)
        time.sleep(rand_delay)

        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        load_more = WebDriverWait(browser, 1000, ignored_exceptions=ignored_exceptions)\
            .until(EC.element_to_be_clickable((By.XPATH, load_button_XPATH)))
        browser.execute_script('arguments[0].click()', load_more)
        
        pages += 1

    except Exception as e:
        print(e)
        break

write_to_file(browser, pages)

