# coding: utf-8

import datetime
from typing import Any, List, Tuple

from ai.api.manager import APIManager
from ai.api.model import Model
from ai.api.result import RequestResult, Usage
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
    
    def _count_tokens(self, text: str) -> int:
        return len(text.split(' '))

    def _send_prompts(self, model: Model, prompts: List[str]) -> Tuple[bool, Any | Exception]:
        prompt_tokens = sum(self._count_tokens(prompt) for prompt in prompts)
        responses = [f"Mock response for prompt {i + 1}" for i in range(len(prompts))]
        completion_tokens = sum(self._count_tokens(response) for response in responses)
        return True, {
            "responses": responses,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        }

    def _response_to_result(self, success: bool, model: str, prompts: List[str], response: Any | Exception):
        return RequestResult(
            success=success,
            prompts=prompts,
            model=model.id,
            responses=response["responses"],
            usage=Usage(
                date=datetime.datetime.now(),
                prompt_tokens=response["usage"]["prompt_tokens"],
                completion_tokens=response["usage"]["completion_tokens"]
            )
        )