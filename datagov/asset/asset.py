# coding: utf-8


class Asset:
    def __init__(self, url, resource_id, name=None):
        self.name = name
        self.url = url
        self.resource_id = resource_id

        self.alleged_size = None
        self.size = None
