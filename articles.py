import requests
from bs4 import BeautifulSoup
from csv import DictWriter, writer, QUOTE_NONNUMERIC
from pathlib import Path
from sentiment_score import get_polarity
import sys
from preprocess import preprocess
import json

class ArticleScraper:
  def __init__(self, website, in_file, out_file) -> None:
    self.website = website
    self.in_file = in_file
    self.out_file = out_file

    if not Path(self.in_file).is_file():
      print("Could not locate {}.".format(self.in_file))
      sys.exit()

    if not Path(self.out_file).is_file():
      ArticleScraper.create_csv(self.out_file)

  def scrape(self):
    article_count = 0
    with open(self.in_file, 'r') as f:
        for line in f:
            article_count += 1
            article_url = line.strip()
            
            with open(self.out_file, 'r') as of:
              if article_url in of.read():
                # print("Article '{}' is already in csv file -- skipping.".format(article_url))
                continue
        
            article = ArticleScraper.scrape_article(self.website, article_url)
            if article is None:
              print("\nArticle {} is empty.\n".format(article_url))
              continue

            sentiment_score = get_polarity(article['content'])
            article['sentiment'] = sentiment_score
            article['text'] = "".join(article['content'].splitlines())
            article['content'] = " ".join(preprocess(article['content']))
            if article['text'] == "" or article['published_at'] == "N\A":
              continue
            ArticleScraper.append_to_csv(self.out_file, article)

  def scrape_article(website_name, article_url):
    if website_name == "bitcoinmagazine":
      return ArticleScraper.scrape_bitcoinmagazine(article_url)
    elif website_name == "cryptoglobe":
      return ArticleScraper.scrape_cryptoglobe(article_url)

  def scrape_cryptoglobe(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    title_container = soup.find("h1", class_="u-heading-v3__title")
    title = title_container.text if title_container else ''

    article_div = soup.find("article", class_="article-container")
    body = ''
    for x in article_div.find_all(["p", "ul", "h3", "h2", "footer"]):
      if x.name == "ul":
        for li in x.find_all("li"):
          li_string = " ".join(li.text.split())
          body += (li_string + " ")
      else:
        body += " ".join(x.text.split()) + ' '
      body += "\n"

    date_script_container = soup.find('script', type='application/ld+json')
    date_script = date_script_container.text if date_script_container else 'N\A'
    date = 'N\A'
    if date_script != 'N\A':
      loaded_date_script = json.loads(date_script)
      if 'datePublished' in loaded_date_script:
        date = loaded_date_script['datePublished'][:10]

    source = "cryptoglobe"

    article = {'url': url,
              'title': title,
              'content': body,
              'published_at': date,
              'source': source
              }
    return article

  def scrape_bitcoinmagazine(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    title_container = soup.find("h1", class_="m-detail-header--title")
    title = title_container.text if title_container else ''

    summary_container = soup.find("div", class_="m-detail-header--dek")
    summary = summary_container.text if summary_container else ''

    article_div = soup.find("div", class_="m-detail--body")

    body = summary
    for x in article_div.find_all(["p", "ul", "h2"]):
      if x.name == "ul":
        for li in x.find_all("li"):
          li_string = " ".join(li.text.split())
          body += (li_string + " ")
      else:
        body += " ".join(x.text.split()) + ' '
      body += "\n"

    date = 'N\A'
    date_container = soup.find("time")
    if date_container:
      date = date_container['datetime'][:10]

    source = "bitcoinmagazine"

    article = {'url': url,
              'title': title,
              'content': body,
              'published_at': date,
              'source': source
              }
    return article

  def append_to_csv(file_path, d):
    csv_header = ['url', 'title', 'content', 'published_at', 'source', 'sentiment', 'text']
    with open(file_path, 'a', newline='') as f_object:
        dictwriter_object = DictWriter(f_object, fieldnames=csv_header, quotechar='"', quoting=QUOTE_NONNUMERIC)
        dictwriter_object.writerow(d)
        f_object.close()

  def create_csv(file_path):
    csv_header = ['url', 'title', 'content', 'published_at', 'source', 'sentiment', 'text']
    with open(file_path, 'w') as f:
      writer_object = writer(f)
      writer_object.writerow(csv_header)
      f.close()