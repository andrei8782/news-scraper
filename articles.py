import requests
from bs4 import BeautifulSoup
from csv import DictWriter, writer
from pathlib import Path
from preprocessing import preprocess
from sentiment_score import get_polarity

def scrape(in_file_path, out_file_path):
  article_count = 0
  with open(in_file_path) as f:
      for line in f:
          article_count += 1
          relative_url = line.strip()
          
          with open(out_file_path) as out_file:
            if relative_url in out_file.read():
              print("Article '{}' is already in csv file -- skipping.".format(relative_url))
              continue
      
          article = scrape_article("bitcoinmagazine", relative_url)
          sentiment_score = get_polarity(article['content'])
          article['sentiment'] = sentiment_score
          article['content'] = " ".join(preprocess(article['content']))
          append_to_csv(out_file_path, article)

def scrape_article(website_name, article_url):
  if website_name == "bitcoinmagazine":
    base_url = "https://bitcoinmagazine.com"
    return scrape_bitcoinmagazine(base_url + article_url)
  
def scrape_bitcoinmagazine(url):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")

  coin_type = "bitcoin"

  title = soup.find("h1", class_="m-detail-header--title").text

  summary_container = soup.find("div", class_="m-detail-header--dek")
  summary = summary_container.text if summary_container else ''

  article_div = soup.find("div", class_="m-detail--body")

  body = summary
  for x in article_div.find_all(["p", "ul", "h2"]):
    if x.name == "ul":
      for li in x.find_all("li"):
        body += (li.text + "; ")
    else:
      body += x.text
    body += "\n"

  date = soup.find("time")['datetime'][:10]
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
  csv_header = ['coin_type', 'url', 'title', 'content', 'published_at', 'source', 'sentiment']
  with open(file_path, 'a', newline='') as f_object:
      dictwriter_object = DictWriter(f_object, fieldnames=csv_header)
      dictwriter_object.writerow(d)
      f_object.close()

def create_csv(file_path):
  csv_header = ['coin_type', 'url', 'title', 'content', 'published_at', 'source', 'sentiment']
  with open(file_path, 'w') as f:
    writer_object = writer(f)
    writer_object.writerow(csv_header)
    f.close()

if __name__ == "__main__":
  in_file_path = "output/bitcoinmagazine/sample_links.txt"
  out_file_path = "output/bitcoinmagazine/articles.csv"

  if not Path(out_file_path).is_file():
    create_csv(out_file_path)

  scrape(in_file_path, out_file_path)