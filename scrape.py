from cryptoglobe_scraper import CryptoglobeScraper
from bitcoinmagazine_scraper import BitcoinmagazineScraper
from articles import ArticleScraper
import sys
import signal
import argparse

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

    def handler(self, signum, frame):
        print("Ctrl-c was pressed. Saving links and exiting without removing tmp_links.")
        if self.link_scraper:
            self.link_scraper.merge_files()
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
        # parser.add_argument('--speed', type=str, required=False)

        args = parser.parse_args()
        self.website = args.website
        self.article_limit = args.limit
        self.ignore_overlap = args.ignore_overlap
    
    def scrape_links(self):
        if self.link_scraper:
            self.link_scraper.scrape_links()
    
    def scrape_articles(self):
        article_scraper = ArticleScraper(self.website)
        article_scraper.scrape()

if __name__ == '__main__':
    scrape_controller = ScrapeController()
    scrape_controller.scrape_links()
    scrape_controller.scrape_articles()
