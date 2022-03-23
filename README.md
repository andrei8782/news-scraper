# news-scraper

## output format
The output files described below will be generated in ```output/$website_name/``` for each scraped website.

```links``` Keeps track of article links added to the database. Stored on the server.

```tmp_links``` Temporarily stores new article links when refreshing the database. Generated on the server but deleted on database update completion.

```articles.csv``` Locally stores the bulk articles when scraping historical data. Then used for adding the entries into the database.

```tmp_articles.csv``` Temporarily stores new articles when refreshing the database. Generated on the server but deleted on database update completion.