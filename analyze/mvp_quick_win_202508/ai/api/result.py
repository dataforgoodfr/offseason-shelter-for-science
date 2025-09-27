# coding: utf-8

import datetime
import time

class Usage:
    def __init__(self, date: datetime = None, prompt_tokens: int = 0, completion_tokens: int = 0, total_tokens: int = 0):
        self.date = date
        self._prompt_tokens = prompt_tokens
        self._completion_tokens = completion_tokens
        self._total_tokens = total_tokens

    def get_prompt_tokens(self) -> int:
        return self._prompt_tokens

    def get_completion_tokens(self) -> int:
        return self._completion_tokens

    def get_total_tokens(self) -> int:
        return self._total_tokens

    def update_tokens(self, prompt_tokens, completion_tokens):
        self.date = datetime.datetime.now()
        self._prompt_tokens += prompt_tokens
        self._completion_tokens += completion_tokens
        self._total_tokens += prompt_tokens + completion_tokens

    def update_from_usage(self, usage: "Usage"):
        self.update_tokens(usage.get_prompt_tokens(), usage.get_completion_tokens())

class RequestResult:
    def __init__(self, success: bool, prompt: str, model: str, response: str, usage: dict, error: str = None):
        self.success = success
        self.prompt = prompt
        self.model = model
        self.response = response
        print(usage)
        self.usage: Usage = Usage(date=time.strftime("%Y-%m-%d %H:%M:%S"), prompt_tokens=usage["prompt_tokens"], completion_tokens=usage["completion_tokens"], total_tokens=usage["total_tokens"])
        self.timestamp = time.time()
        self.error = error