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

class Gpt4_1(Model):
    def __init__(self):
        super().__init__("gpt-4.1", "gpt-4.1", 2., 8.)

class Gpt4_1_Nano(Model):
    def __init__(self):
        super().__init__("gpt-4.1-nano", "gpt-4.1-nano", 0.1, 0.4)

class Gpt4_1_Mini(Model):
    def __init__(self):
        super().__init__("gpt-4.1-mini", "gpt-4.1-mini", 0.4, 1.6)

class Gpt4o(Model):
    def __init__(self):
        super().__init__("gpt-4o", "gpt-4", 2.5, 10.)

class Gpt4oMini(Model):
    def __init__(self):
        super().__init__("gpt-4o-mini", "gpt-4-mini", 0.15, 0.6)