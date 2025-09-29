# coding: utf-8

from ai.api.model import Model

class Mock1(Model):
    def __init__(self):
        super().__init__("mock-1", "mock-1", 0.25, 0.5)

class Mock2(Model):
    def __init__(self):
        super().__init__("mock-2", "mock-2", 0.5, 1)

class Mock3(Model):
    def __init__(self):
        super().__init__("mock-3", "mock-3", 15, 200)