# coding: utf-8

from typing import Any

from ai.api.manager import APIManager
from ai.api.model import Model
from ai.api.result import RequestResult
from ai.api.mock.model import Mock1, Mock2, Mock3

AVAILABLE_MODELS = [
    Mock1,
    Mock2,
    Mock3,
]

DEFAULT_MODEL_ID = "mock-1"

class MockManager(APIManager):
    def __init__(self):
        super().__init__()

        self._build_model_dict(AVAILABLE_MODELS)

    def get_name(self) -> str:
        return "Mock"

    def get_api(self) -> Any:
        return None

    def get_api_key_env_var(self) -> str:
        return "MOCK_API_KEY"

    def get_default_model_id(self) -> str:
        return DEFAULT_MODEL_ID

    def _send_prompt(self, model: Model, prompt: str) -> RequestResult:
        prompt_tokens = len(prompt.split(' '))
        return RequestResult(
            success=True,
            prompt=prompt,
            model=model.id,
            response=f"Mock response from {model.id}",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": 10,
                "total_tokens": prompt_tokens + 10
            }
        )