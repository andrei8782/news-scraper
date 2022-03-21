from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import sys
from pathlib import Path

class LinkScraper:
    available_websites = ['cryptoglobe']

    def __init__(self, website, article_limit=sys.maxsize):
        if not self.is_website_compatible(website):
            print("Website not supported yet. Exiting.\n")
            print("Available websites: {}.".format(self.available_websites))
            sys.exit()
        
        self.article_limit = article_limit

        self.setup_paths(website)
        self.setup_output_files()

        chrome_options = Options() 
        # chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.get(self.url)
        
        self.last_height = 0
        self.current_height = self.browser.execute_script("return document.body.scrollHeight")
        self.page_num = 1

    def is_website_compatible(self, website):
        if website in self.available_websites:
            return True
        else:
            return False

    def setup_paths(self, website):
        self.website = website
        if website == 'cryptoglobe':
            self.url = "https://www.cryptocompare.com/news/list/latest/?feeds=cryptoglobe"

        self.tmp_filepath = "output/" + self.website + "/tmp_links"
        self.links_filepath = "output/" + self.website + "/links"

    def setup_output_files(self):
        lf = Path(self.links_filepath)
        lf.touch(exist_ok=True)
        tmp_lf = Path(self.tmp_filepath)
        tmp_lf.touch(exist_ok=True)

    def parse_links(self):
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        list = soup.find_all("div", class_="item-news ng-scope") 
        new_links = []     
        for div in list:
            heading = div.find("h3")
            link = heading.find("a", class_="ng-binding")['href']
            if link == '':
                continue
            else:
                new_links.append(link)
        return new_links

    def reached_end_of_webpage(self):
        if self.current_height == self.last_height:
            return True
        else:
            return False

    def render_page(self):
        self.last_height = self.current_height
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        self.current_height = self.browser.execute_script("return document.body.scrollHeight")

    def scrape_links(self):
        lf = open(self.links_filepath, 'r')
        all_links = lf.read()
        lf.close()

        link_overlap = False
        article_limit_reached = False 
        while not self.reached_end_of_webpage() and link_overlap == False and article_limit_reached == False:
            print("Page {} loaded.".format(self.page_num))

            links = self.parse_links()
            print("{} links have been parsed.".format(len(links)))
            # print("Links on page {} are:\n{}".format(self.page_num, links))
            LinkScraper.remove_file(self.tmp_filepath, silent=True)
            for lnum, link in enumerate(links):
                if link in all_links:
                    print("Link {} already present in {}. csv up to date.".format(link, self.links_filepath))
                    link_overlap = True
                    break
                else:
                    LinkScraper.append_to_file(self.tmp_filepath, link)
                    if (lnum + 1) == self.article_limit:
                        print("Scraped {} links. Finishing up.".format(article_limit))
                        article_limit_reached = True
                        break
            
            self.render_page()
            self.page_num += 1
        
        self.merge_files()
        # TODO: update database
        LinkScraper.remove_file(self.tmp_filepath)

    def append_to_file(file_path, str):
        with open(file_path, "a") as f:
            f.write(str + '\n')

    def merge_files(self):
        with open(self.links_filepath, "a") as lf:
            with open(self.tmp_filepath, "r") as tmpf:
                for line in tmpf:
                    lf.write(line)
        print("Merged {} into {}.".format(self.tmp_filepath, self.links_filepath))

    def remove_file(file_path, silent=False):
        if os.path.exists(file_path):
            os.remove(file_path)
            if not silent:
                print("Removed {}.".format(file_path))
        else:
            print("The file {} does not exist!".format(file_path))

    def parse_args(args):
        article_limit = None
        if len(sys.argv) == 1:
            print("Please specify which website to scrape.")
            sys.exit()
        elif len(sys.argv) >= 2:
            if not isinstance(sys.argv[1], str):
                print("Please specify a string website")
                sys.exit()           
            if len(sys.argv) >= 3:
                article_limit = int(args[2]) if args[2].isdecimal() else None
                if article_limit is None:
                    print("Please specify an integer article limit")
                    sys.exit()           

        website = args[1]
        return website, article_limit

if __name__ == "__main__":
    website, article_limit = LinkScraper.parse_args(sys.argv)
    link_scraper = LinkScraper(website, article_limit)
    link_scraper.scrape_links()