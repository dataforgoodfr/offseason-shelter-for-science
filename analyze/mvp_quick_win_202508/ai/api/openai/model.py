# coding: utf-8

from ai.api.model import Model

# Pricing: https://platform.openai.com/docs/pricing

class Gpt5Nano(Model):
    def __init__(self):
        super().__init__("gpt-5-nano", "gpt-5-nano", 0.05, 0.4)

class Gpt5Mini(Model):
    def __init__(self):
        super().__init__("gpt-5-mini", "gpt-5-mini", 0.25, 2)

class Gpt5(Model):
    def __init__(self):
        super().__init__("gpt-5", "gpt-5", 1.25, 10)

