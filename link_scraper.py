from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import sys
from pathlib import Path

class LinkScraper:
    def __init__(self, website, article_limit=sys.maxsize, ignore_overlap=False):
        self.article_limit = article_limit
        self.ignore_overlap = ignore_overlap
        self.setup_paths(website)
        self.setup_output_files()

        chrome_options = Options() 
        # chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.get(self.url)
        self.page_num = 1

    def setup_paths(self, website):
        self.website = website
        if website == 'cryptoglobe':
            self.url = "https://www.cryptocompare.com/news/list/latest/?feeds=cryptoglobe"
        elif website == 'bitcoinmagazine':
            self.url = "https://bitcoinmagazine.com/articles"

        self.tmp_filepath = "output/" + self.website + "/tmp_links"
        self.links_filepath = "output/" + self.website + "/links"

    def setup_output_files(self):
        lf = Path(self.links_filepath)
        lf.touch(exist_ok=True)
        tmp_lf = Path(self.tmp_filepath)
        tmp_lf.touch(exist_ok=True)

    def scrape_links(self):
        lf = open(self.links_filepath, 'r')
        all_links = lf.read()
        lf.close()

        link_overlap = False
        article_limit_reached = False 
        while not self.reached_end_of_webpage() and link_overlap == False and article_limit_reached == False:
            print("Page {} loaded.".format(self.page_num))

            links = self.parse_links()
            if links is None:
                print("No links could be parsed. Aborting.")
                break
            print("{} links have been parsed.".format(len(links)))
            # print("Links on page {} are:\n{}".format(self.page_num, links))
            LinkScraper.clear_file(self.tmp_filepath)
            for lnum, link in enumerate(links):
                if link in all_links:
                    print("Link {} already present in {}.".format(link, self.links_filepath))
                    if self.ignore_overlap == False:
                        link_overlap = True
                        break
                    else:
                        continue
                else:
                    LinkScraper.append_to_file(self.tmp_filepath, link)
                    if (lnum + 1) == self.article_limit:
                        print("Scraped {} links. Finishing up.".format(self.article_limit))
                        article_limit_reached = True
                        break
            
            self.render_page()
            self.page_num += 1
            # print("DEBUG:\nreached end of page: {}\nlink_overlap: {}\narticle_limit_reached: {}.\n".format(self.reached_end_of_webpage(), link_overlap, article_limit_reached))
        
        self.merge_files()
        # TODO: update database
        LinkScraper.remove_file(self.tmp_filepath)

    def append_to_file(file_path, str):
        with open(file_path, "a") as f:
            f.write(str + '\n')

    def merge_files(self):
        merged_lines = 0
        with open(self.links_filepath, "a") as lf:
            with open(self.tmp_filepath, "r") as tmpf:
                for line in tmpf:
                    lf.write(line)
                    merged_lines += 1
        print("Merged {} into {}.\n{} links added.".format(self.tmp_filepath, self.links_filepath, merged_lines))

    def remove_file(file_path, silent=False):
        if os.path.exists(file_path):
            os.remove(file_path)
            if not silent:
                print("Removed {}.".format(file_path))
        else:
            print("The file {} does not exist!".format(file_path))

    def clear_file(file_path):
        with open(file_path,'w') as f:
            pass