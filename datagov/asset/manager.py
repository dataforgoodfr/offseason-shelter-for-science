# coding: utf-8
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from collector import Collector, ScrapyCollector
from link_scraper import LinkScraperCollector

class Manager:
    def __init__(self, settings: dict):
        collectors = [LinkScraperCollector]
        self._collectors = {}
        self.process = CrawlerProcess(settings)
        
        for collector_cls in collectors:
            obj = collector_cls()
            obj_type = obj.__module__ + "." + obj.__class__.__qualname__
            obj.attach_process(self.process)
            self._collectors[obj_type] = obj
            
        self.collect_count = 0
        self.collect_progress = None

    def get_collector(self, url):
        for collector in self._collectors.values():
            if collector.check_url(url):
                return collector
        return None

    def collect_later(self, url, collection_name=None, collection_key=None):
        result = False
        collector = self.get_collector(url)
        if collector:
            collector.collect(
                url, collection_name=collection_name, collection_key=collection_key
            )
            self.collect_count += 1
            result = True
        return result

    def collect(self, progress=False):
        if progress:
            from tqdm import tqdm
            self.collect_progress = tqdm(
                total=self.collect_count, desc="Collecting links and files"
            )
            
            for crawler in self.process.crawlers:
                crawler.signals.connect(
                    self._on_spider_closed, signal=signals.spider_closed
                )
        
        self.process.start()
        
        if progress:
            self.collect_progress.close()

    def _on_spider_closed(self, spider, reason):
        if self.collect_progress:
            self.collect_progress.update()
