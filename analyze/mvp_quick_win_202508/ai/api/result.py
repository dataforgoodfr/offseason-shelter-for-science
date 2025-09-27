# coding: utf-8

import time

class Usage:
    def __init__(self, date: str, prompt_tokens: int, completion_tokens: int, total_tokens: int):
        self.date = date
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens

class RequestResult:
    def __init__(self, success: bool, prompt: str, model: str, response: str, usage: dict, error: str = None):
        self.success = success
        self.prompt = prompt
        self.model = model
        self.response = response
        self.usage = Usage(date=time.strftime("%Y-%m-%d %H:%M:%S"), prompt_tokens=usage["prompt_tokens"], completion_tokens=usage["completion_tokens"], total_tokens=usage["total_tokens"])
        self.timestamp = time.time()
        self.error = error