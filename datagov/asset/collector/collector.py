# coding: utf-8


class Collector:
    def check_url(self, url):
        return True

    def collect(self, url, collection_name=None, collection_key=None):
        if self.check_url(url):
            self.url = url

            self.collection_name = collection_name
            self.collection_key = collection_key

            self._before_collect()
            self._collect()
            self._after_collect()

    def _before_collect(self):
        pass

    def _after_collect(self):
        pass


class ScrapyCollector(Collector):
    def __init__(self):
        self.item_pipelines = {}
