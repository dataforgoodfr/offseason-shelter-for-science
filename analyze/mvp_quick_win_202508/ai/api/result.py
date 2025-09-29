# coding: utf-8

import datetime
import json
import pathlib
import time
from typing import Dict, List

class Usage:
    @classmethod
    def load(cls, path: pathlib.Path) -> "Usage":
        if not path.exists():
            result = cls()
        else:
            with open(path, "r") as f:
                usage = json.load(f)
                result = cls(
                    datetime.datetime.fromisoformat(usage["date"]),
                    usage["prompt"],
                    usage["completion"]
                    )

        return result

    def __init__(self, date: datetime = None, prompt_tokens: int = 0, completion_tokens: int = 0):
        self.date = date
        self._prompt_tokens = prompt_tokens
        self._completion_tokens = completion_tokens
        self._total_tokens = prompt_tokens + completion_tokens

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

    def save(self, path: pathlib.Path):
        with path.open("w") as f:
            json.dump(self.to_dict(), f)

    def to_dict(self) -> Dict[str, str | int]:
        return {
                "date": self.date.isoformat(),
                "prompt": self._prompt_tokens,
                "completion": self._completion_tokens,
            }

class RequestResult:
    def __init__(self, success: bool, prompts: List[str], model: str, responses: List[str], usage: Usage, error: str = None):
        self.success = success
        self.prompts = prompts
        self.model = model
        self.responses = responses
        self.usage: Usage = usage
        self.timestamp = time.time()
        self.error = error
        self.context: Dict = None

    def to_dict(self) -> Dict:
        result = {
            "success": self.success,
            "model": self.model,
            "prompts": self.prompts,
            "usage": self.usage.to_dict(),
            "responses": self.responses,
        }
        if self.error:
            result["error"] = self.error

        if self.context:
            result["context"] = self.context

        return result