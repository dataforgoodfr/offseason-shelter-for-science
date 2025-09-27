import os
import getpass
from openai import OpenAI
import time

from ai.api.manager import APIManager
from ai.api.model import Model
from ai.api.result import RequestResult

from ai.api.openai.model import Gpt5Nano, Gpt5Mini

AVAILABLE_MODELS = [
    "gpt-4",
    "gpt-4-turbo",
    Gpt5Nano,
    Gpt5Mini
]

DEFAULT_MODEL_ID = "gpt-5-nano"

class OpenAIManager(APIManager):
    def __init__(self):
        super().__init__()
        self.client = None

        self._build_model_dict(AVAILABLE_MODELS)

    def get_name(self) -> str:
        return "OpenAI"

    def get_default_model_id(self) -> str:
        return DEFAULT_MODEL_ID

    def get_api_key_env_var(self) -> str:
        return "OPENAI_API_KEY"

    def get_api(self) -> OpenAI:
        return self.client

    def _send_prompt(self, model: Model, prompt: str) -> RequestResult:
        if self.client is None:
            self.client = OpenAI(api_key=self._get_api_key())

        if model.id not in AVAILABLE_MODELS:
            raise ValueError(f"Model {model.id} not found")

        try:
            response = self.client.chat.completions.create(
                model=model.id,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            return RequestResult(
                success=True,
                prompt=prompt,
                model=model.id,
                response=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
        
        except Exception as e:
            return RequestResult(
                success=False,
                prompt=prompt,
                model=model.id,
                error=str(e)
            )