# http://api.springer.com/meta/v2/json?api_key=f5dbe2907349beb0116087e6b4e98144&q=sort%3Adate+pub%3A%22Nature%20Materials%22&s=1&p=100
# "Article" in genre

import scrapy
import json
from bs4 import BeautifulSoup
from paper_spider.items import PaperItem, SpringerSearchItem

class PaperSpider(scrapy.Spider):
    name = "paper"

    def start_requests(self):
        self.journal_name = 'Nature Materials'
        for page in range(1, 75):
            url = f'https://www.nature.com/nmat/research-articles?searchType=journalSearch&sort=PubDate&type=article&page={page}'
            yield scrapy.Request(url, self.parse_articles)
        # total = 5196
        # p = 100
        # for s in range(1, int(total / p) + 1):
        #     url = f'http://api.springer.com/meta/v2/json?api_key=f5dbe2907349beb0116087e6b4e98144&q=sort:date%20pub:"{self.journal_name}"&s={s}&p={p}'
        #     yield scrapy.Request(url, self.parse)

    def parse_articles(self, response):
        journal_name = "Nature Materials"
        soup =  BeautifulSoup(response.text, 'html.parser')
        article_list = soup.find('section', {'id': 'new-article-list'}).div.ul
        for li in article_list.find_all('li', recursive=False):
            a = li.find('a')
            title = a.text
            url = f'http://api.springer.com/meta/v2/json?api_key=f5dbe2907349beb0116087e6b4e98144&q=pub:"{journal_name}" title:"{title}"&s=1&p=10'
            self.logger.info(f'Find record of {title}')
            yield SpringerSearchItem(url=url, title=title)

    def parse(self, response):
        records = json.loads(response.text)['records']
        for record in records:
            if record['title'].lower() != response.request.meta['title'].lower():
                continue
            paper_item = PaperItem(
                journal=self.journal_name,
                title=record['title'],
                abstract=record['abstract'],
                identifier=record['identifier'],
                online_date=record['onlineDate']
            )
            # self.logger.info(f'Yield record of {record["title"]}')
            yield paper_item
