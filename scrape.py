from cryptoglobe_scraper import CryptoglobeScraper
from bitcoinmagazine_scraper import BitcoinmagazineScraper
from articles import ArticleScraper
from link_scraper import LinkScraper
import sys
import signal
import argparse
from append_db import DatabaseController

class ScrapeController():
    available_websites = ['bitcoinmagazine', 'cryptoglobe']

    def __init__(self) -> None:
        signal.signal(signal.SIGINT, self.handler)

        self.parse_args()

        if not self.is_website_compatible():
            print("Website not supported yet.")
            print("Available websites: {}.".format(self.available_websites))
            sys.exit()

        self.link_scraper = None
        if self.website == 'cryptoglobe':
            self.link_scraper = CryptoglobeScraper(self.article_limit, self.ignore_overlap)
        elif self.website == 'bitcoinmagazine':
            self.link_scraper = BitcoinmagazineScraper(self.article_limit, self.ignore_overlap)
        
        self.tmp_articles_path = "output/" + self.website + "/tmp_articles.csv"
        self.tmp_links_path = "output/" + self.website + "/tmp_links"
        self.articles_path = "output/" + self.website + "/articles.csv"
        self.links_path = "output/" + self.website + "/links"

    def handler(self, signum, frame):
        print("Ctrl-c was pressed. Saving links and exiting without removing tmp_links.")
        if self.link_scraper:
            self.link_scraper.merge_files()
            self.link_scraper.browser.quit()
        sys.exit()

    def is_website_compatible(self):
        if self.website in self.available_websites:
            return True
        else:
            return False

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-w', '--website', type=str, required=True, help="Website name")
        parser.add_argument('-l', '--limit', type=int, help="Article limit")
        parser.add_argument('-i', '--ignore_overlap', action='store_true', help="Ignore overlapping articles already present in links")
        parser.add_argument('-r', '--refresh', action='store_true', help="Indicate refresh functionality")
        # parser.add_argument('--speed', type=str, required=False)

        args = parser.parse_args()
        self.website = args.website
        self.article_limit = args.limit
        self.ignore_overlap = args.ignore_overlap
        self.refresh_flag = args.refresh
    
    def scrape_links_locally(self):
        if self.link_scraper:
            self.link_scraper.scrape_links()
            # self.link_scraper.merge_files()
            self.link_scraper.browser.quit()
            # LinkScraper.remove_file(self.tmp_links_path)
    
    def scrape_articles(self, in_file, out_file):
        article_scraper = ArticleScraper(self.website, in_file, out_file)
        article_scraper.scrape()
        print("Scraped {} articles.".format(article_scraper.article_count))

    def scrape_locally(self):
        # self.scrape_links_locally()
        self.scrape_articles(in_file=self.tmp_links_path, out_file=self.articles_path)

    def refresh(self):
        print("Refreshing the database...")
        if self.link_scraper:
            self.link_scraper.scrape_links()
            self.link_scraper.browser.quit()

            self.scrape_articles(in_file=self.tmp_links_path, out_file=self.tmp_articles_path)

            db_controller = DatabaseController()
            append_successful = db_controller.append_to_db(self.tmp_articles_path)
            if append_successful:
                self.link_scraper.merge_files()
            
            LinkScraper.remove_file(self.tmp_links_path)
            LinkScraper.remove_file(self.tmp_articles_path) 
        else:
            print("link_scraper object is not instantiated.")

if __name__ == '__main__':
    scrape_controller = ScrapeController()
    if scrape_controller.refresh_flag:
        scrape_controller.refresh()
    else:
        scrape_controller.scrape_locally()