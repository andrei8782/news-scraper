from bs4 import BeautifulSoup
import time
from link_scraper import LinkScraper

class CryptoglobeScraper(LinkScraper):
    def __init__(self, article_limit=None, ignore_overlap=False) -> None:
        super().__init__("cryptoglobe", article_limit, ignore_overlap)
        self.last_height = 0
        self.current_height = self.browser.execute_script("return document.body.scrollHeight")
        
    def render_page(self):
        self.last_height = self.current_height
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        self.current_height = self.browser.execute_script("return document.body.scrollHeight")

    def parse_links(self):
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        list = soup.find_all("div", class_="item-news ng-scope") 
        links = []     
        for div in list:
            heading = div.find("h3")
            link = heading.find("a", class_="ng-binding")['href']
            if link == '':
                continue
            else:
                links.append(link)
        return links

    def reached_end_of_webpage(self):
        if self.current_height == self.last_height:
            return True
        else:
            return False