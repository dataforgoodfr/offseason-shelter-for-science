# coding: utf-8
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from collector import Collector, ScrapyCollector
from link_scraper import LinkScraperCollector
from redis_cache import RedisUrlCache
import logging

logger = logging.getLogger(__name__)

class Manager:
    def __init__(self, settings: dict, redis_config: dict = None):
        collectors = [LinkScraperCollector]
        self._collectors = {}
        self.process = CrawlerProcess(settings)
        
        # Initialisation du cache Redis
        redis_config = redis_config or {}
        self.url_cache = RedisUrlCache(
            redis_host=redis_config.get('host', 'redis'),
            redis_port=redis_config.get('port', 6379),
            redis_db=redis_config.get('db', 0),
            redis_password=redis_config.get('password'),
            expiry_hours=redis_config.get('expiry_hours', 24)
        )
        
        for collector_cls in collectors:
            obj = collector_cls()
            obj_type = obj.__module__ + "." + obj.__class__.__qualname__
            obj.attach_process(self.process)
            self._collectors[obj_type] = obj
            
        self.collect_count = 0
        self.collect_progress = None
        self.skipped_count = 0

    def get_collector(self, url):
        for collector in self._collectors.values():
            if collector.check_url(url):
                return collector
        return None

    def collect_later(self, url, collection_name=None, collection_key=None):
        
        if self.url_cache.is_url_scraped(url):
            logger.info(f"URL déjà scrapée (cache): {url}")
            self.skipped_count += 1
            return True  
        
        result = False
        collector = self.get_collector(url)
        if collector:
            # Marquer comme en cours de traitement
            metadata = {
                'collection_key': collection_key,
                'collection_name': collection_name,
                'status': 'scheduled'
            }
            
            # Marquer dans le cache (avec statut "scheduled")
            self.url_cache.mark_url_scraped(url, metadata)
            logger.info(f"Scraping programmé et mis en cache: {url}")
            
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
        
        if self.collect_count > 0:
            self.process.start()
        else:
            logger.info("Aucune nouvelle URL à traiter")
        
        if progress:
            self.collect_progress.close()

    def _on_spider_closed(self, spider, reason):
        if self.collect_progress:
            self.collect_progress.update()

    def clear_cache(self):
        """Vide le cache Redis"""
        return self.url_cache.clear_cache()
    
    def get_cache_stats(self):
        """Retourne les statistiques du cache"""
        return self.url_cache.get_cache_stats()