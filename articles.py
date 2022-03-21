import requests
from bs4 import BeautifulSoup
from csv import DictWriter, writer, QUOTE_NONNUMERIC
from pathlib import Path
from sentiment_score import get_polarity
import sys
from preprocess import preprocess
import json

def scrape(website_name):
  in_file = "output/" + website_name + "/sample_links"
  out_file = "output/" + website_name + "/sample_articles.csv"

  article_count = 0
  with open(in_file) as f:
      for line in f:
          article_count += 1
          relative_url = line.strip()
          
          with open(out_file) as of:
            if relative_url in of.read():
              print("Article '{}' is already in csv file -- skipping.".format(relative_url))
              continue
      
          article = scrape_article(website_name, relative_url)
          if article is None:
            print("\nArticle {} is empty.\n".format(relative_url))
            continue

          sentiment_score = get_polarity(article['content'])
          article['sentiment'] = sentiment_score
          article['text'] = "".join(article['content'].splitlines())
          article['content'] = " ".join(preprocess(article['content']))
          append_to_csv(out_file, article)

def scrape_article(website_name, article_url):
  if website_name == "bitcoinmagazine":
    base_url = "https://bitcoinmagazine.com"
    return scrape_bitcoinmagazine(base_url + article_url)
  elif website_name == "cryptoglobe":
    return scrape_cryptoglobe(article_url)

def scrape_cryptoglobe(url):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")
  coin_type = "N/A"

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

  print(body)

  date_script_container = soup.find('script', type='application/ld+json')
  date_script = date_script_container.text if date_script_container else 'N\A'
  date = 'N\A'
  if date_script != 'N\A':
    loaded_date_script = json.loads(date_script)
    if 'datePublished' in loaded_date_script:
      date = loaded_date_script['datePublished'][:10]

  source = "cryptoglobe"

  article = {'coin_type': coin_type, 
             'url': url,
             'title': title,
             'content': body,
             'published_at': date,
             'source': source
             }
  return article

def scrape_bitcoinmagazine(url):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")

  coin_type = "bitcoin"

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

  article = {'coin_type': coin_type, 
             'url': url,
             'title': title,
             'content': body,
             'published_at': date,
             'source': source
             }
  return article

def append_to_csv(file_path, d):
  csv_header = ['coin_type', 'url', 'title', 'content', 'published_at', 'source', 'sentiment', 'text']
  with open(file_path, 'a', newline='') as f_object:
      dictwriter_object = DictWriter(f_object, fieldnames=csv_header, quotechar='"', quoting=QUOTE_NONNUMERIC)
      dictwriter_object.writerow(d)
      f_object.close()

def create_csv(file_path):
  csv_header = ['coin_type', 'url', 'title', 'content', 'published_at', 'source', 'sentiment', 'text']
  with open(file_path, 'w') as f:
    writer_object = writer(f)
    writer_object.writerow(csv_header)
    f.close()

if __name__ == "__main__":
  available_websites = ['bitcoinmagazine', 'cryptoglobe']

  args = sys.argv
  if len(args) == 1:
    print("Please specify which website to scrape.")
    sys.exit()
  elif len(args) > 2:
    print("Please specify a single website to scrape.")
    sys.exit()
  elif args[1] not in available_websites:
    print("Website not supported yet.")
    sys.exit()

  website_name = args[1]
  in_file = "output/" + website_name + "/sample_links"
  out_file = "output/" + website_name + "/sample_articles.csv"

  if not Path(in_file).is_file():
    print("Could not locate {}.".format(in_file))
    sys.exit()

  if not Path(out_file).is_file():
    create_csv(out_file)

  scrape(website_name)