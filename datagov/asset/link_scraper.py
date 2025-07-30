
# coding: utf-8
from collector import ScrapyCollector
from spiders.link_spider import LinkSpider
from scrapy.crawler import CrawlerProcess

class LinkScraperCollector(ScrapyCollector):
    def __init__(self):
        super().__init__()

    def check_url(self, url) -> bool:
        # Accepter toutes les URLs HTTP/HTTPS
        return url.startswith(('http://', 'https://'))

    def attach_process(self, process: CrawlerProcess):
        self.process = process

    def _collect(self):
        self.process.crawl(
            LinkSpider,
            url=self.url,
            collection_name=self.collection_name,
            collection_key=self.collection_key,
        )