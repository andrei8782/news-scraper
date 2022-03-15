import requests
from bs4 import BeautifulSoup

URL = "https://bitcoinmagazine.com/culture/pierre-rochard-lightning-adoption-will-basically-mirror-bitcoin-adoption"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

coin_type = "bitcoin" + '\n'

url = URL + '\n'

title = soup.find("h1", class_="m-detail-header--title").text + '\n'

summary_container = soup.find("div", class_="m-detail-header--dek")
summary = ''
if summary_container:
  summary = summary_container.text

article_div = soup.find("div", class_="m-detail--body")

body = '' + summary + "\n\n"
for x in article_div.find_all(["p", "ul", "h2"]):
  if x.name == "ul":
    for li in x.find_all("li"):
      body += li.text
      body += ", "
  else:
    body += x.text
  body += "\n\n"

date = soup.find("time").text + '\n'
source = "bitcoinmagazine" + '\n'

print(coin_type)
print(url)
print(title)
print(body)
print(date)
print(source)