# coding: utf-8

class Organization:
    def __init__(self, obj=None):
        self.obj = obj

        self.id = obj['id']
        self.name = obj['name']
        self.title = obj['title']
        self.created = obj['created']