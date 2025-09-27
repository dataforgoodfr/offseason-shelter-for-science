# coding: utf-8

import json
from pathlib import Path
from typing import List

from ai.api.result import Usage

class Model:
    usage_directory = Path(__file__).parent.parent / "data" / "usage"

    @classmethod
    def get_usage_directory(cls) -> Path:
        return cls.usage_directory

    @classmethod
    def set_usage_directory(cls, usage_directory: Path):
        cls.usage_directory = usage_directory

    def __init__(self, id: str, name: str, input_cost: float = None, output_cost: float = None):
        """
        Initialize a model.

        Args:
            id: The model id.
            name: The model name.
            input_cost: cost / 1M input tokens.
            output_cost: cost / 1M output tokens.
        """
        self.id = id
        self.name = name
        self.input_cost = input_cost
        self.output_cost = output_cost

        self.usage = None
        self.usage_logs: List[Usage] = []
        
        self.load_usage()

    def get_usage_file_path(self) -> Path:
        return self.get_usage_directory() / f"{self.id}.json"

    def load_usage(self) -> Usage | None:
        if self.usage is not None:
            return self.usage

        file_path = self.get_usage_file_path()
        if not file_path.exists():
            return None

        with open(file_path, "r") as f:
            self.usage = Usage(**json.load(f))

        return self.usage

    def save_usage(self) -> None:
        file_path = self.get_usage_file_path()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(self.usage.__dict__, f)

    def update_usage(self, usage: Usage):
        self.add_usage_log(usage)

        self.usage.prompt_tokens += usage.prompt_tokens
        self.usage.completion_tokens += usage.completion_tokens
        self.usage.total_tokens += usage.total_tokens

    def add_usage_log(self, usage: Usage):
        self.usage_logs.append(usage)

    def estimate_input_spending(self) -> float:
        if self.input_cost is None:
            raise ValueError("Input cost is not set")

        result = self.input_cost * self.usage.prompt_tokens / 1000000
        print(f"Input spending for {self.id}: {result}")

        return result

    def estimate_output_spending(self) -> float:
        if self.output_cost is None:
            raise ValueError("Output cost is not set")

        result = self.output_cost * self.usage.completion_tokens / 1000000
        print(f"Output spending for {self.id}: {result}")

        return result

    def estimate_spending(self) -> float:
        return self.estimate_input_spending() + self.estimate_output_spending()
