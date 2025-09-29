import datetime
import json
from typing import Any, List, Tuple

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from ai.api.manager import APIManager
from ai.api.model import Model
from ai.api.result import RequestResult, Usage

from ai.api.openai.model import Gpt4_1_Nano, Gpt4_1_Mini, Gpt5Nano, Gpt5Mini

AVAILABLE_MODELS = [
    Gpt4_1_Nano,
    Gpt4_1_Mini,
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

    def _send_prompts(self, model: Model, prompts: List[str]) -> Tuple[bool, Any | Exception]:
        success = False
        response = None

        if self.client is None:
            self.client = OpenAI(api_key=self._get_api_key())

        try:
            response = self.client.chat.completions.create(
                model=model.id,
                messages=[{"role": "user", "content": prompt} for prompt in prompts],
                # temperature=0.7,
            )
            success = True
            self._save_output("openai_response", json.dumps(response, indent=2, default=vars, ensure_ascii=False), ext="json")

        except Exception as e:
            success = False
            response = e

        return success, response

    def _response_to_result(self, success: bool, model: Model, prompts: List[str], response: Any | Exception) -> RequestResult:
        error = None
        usage = None
        model = model.id
        if not success:
            error = response if not success else None
            responses = ["ERROR"]
        else:
            if type(response) is ChatCompletion:
                usage = Usage(
                    date=datetime.datetime.now(),
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens
                )
                model = response.model
                responses = [choice.message.content for choice in response.choices]
            else:
                raise ValueError(f"Unexpected response type from OpenAI API: {type(response)}")

        return RequestResult(
                success=success,
                prompts=prompts,
                model=model,
                responses=responses,
                usage=usage,
                error=error
            )