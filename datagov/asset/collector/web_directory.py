# coding: utf-8

from .collector import ScrapyCollector

import re

from twisted.internet import asyncioreactor

asyncioreactor.install()

from scrapy.crawler import CrawlerProcess
from .spiders import WebDirectorySpider


class WebDirectory(ScrapyCollector):
    def __init__(self, modified_col: int, size_col: int):
        super().__init__()

        self.modified_col = modified_col
        self.size_col = size_col

    def attach_process(self, process: CrawlerProcess):
        self.process = process

    def _collect(self):
        self.process.crawl(
            WebDirectorySpider,
            url=self.url,
            modified_col=self.modified_col,
            size_col=self.size_col,
            collection_name=self.collection_name,
            collection_key=self.collection_key,
        )


# -----


class NOAAWebDirectory(WebDirectory):
    def __init__(self):
        super().__init__(1, 2)

        self._compile_regex()

    def check_url(self, url) -> bool:
        return self.regex.match(url)

    def _compile_regex(self):
        self.regex = re.compile(self._get_regex())

    def _get_regex(self) -> str:
        raise NotImplementedError()


# -----


class NCEIWebDirectory(NOAAWebDirectory):
    def _get_regex(self):
        return r"^https://www.ncei.noaa.gov/pub/data/.+/$"
