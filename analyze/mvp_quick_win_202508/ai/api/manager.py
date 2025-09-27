# coding: utf-8

from abc import ABC, abstractmethod
import getpass
import importlib
import os
from typing import Any, Dict, List

from .model import Model
from .result import RequestResult

_MANAGERS = {
    "openai": "ai.api.openai.manager.OpenAIManager",
    "mock": "ai.api.mock.manager.MockManager"
}

# API Manager Interface
class APIManagerInterface(ABC):

    @abstractmethod
    def get_default_model_id(self) -> str:
        """Returns the default model id."""
        pass

    def get_default_model(self) -> Model:
        """Returns the default model."""
        pass

    @abstractmethod
    def get_available_models(self) -> Dict[str, Model]:
        """Returns the available models."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the API manager."""
        pass
    
    @abstractmethod
    def get_api(self) -> Any:
        """Returns the API client."""
        pass
    
    @abstractmethod
    def get_api_key_env_var(self) -> str:
        """Returns the environment variable name for the API key."""
        pass

    @abstractmethod
    def init(self) -> Any:
        """Initializes the API manager."""
        pass

    @abstractmethod
    def set_spending_estimator(self):
        """Defines the Spending Estimator."""
        pass

    @abstractmethod
    def send_prompt(self, model_id: str, prompt: str) -> RequestResult:
        """Sends a prompt to the API and returns the result."""
        pass

    @abstractmethod
    def estimate_spending(self) -> float:
        """Estimates the spending for the API manager."""
        pass

def _create_manager(manager_name: str) -> APIManagerInterface:
    if manager_name not in _MANAGERS:
        raise ValueError(f"Manager {manager_name} not found")

    target_path = _MANAGERS[manager_name]
    module_path, class_name = target_path.rsplit(".", 1)

    module = importlib.import_module(module_path)
    manager_class = getattr(module, class_name)
    return manager_class()

_INSTANCES = {}

def get_instance(manager_name: str) -> APIManagerInterface:
    if manager_name in _MANAGERS and manager_name not in _INSTANCES:
        _INSTANCES[manager_name] = _create_manager(manager_name)
    
    return _INSTANCES[manager_name]

def get_instances() -> Dict[str, APIManagerInterface]:
    return {manager_name: get_instance(manager_name) for manager_name in _MANAGERS}

# ------------------------------------------------------------------------------------------------

from .spending import SpendingEstimator

# Abstract class for API managers
class APIManager(APIManagerInterface):
    def __init__(self):
        self.models = {}
        self.spending_estimator = None

    def get_default_model(self) -> Model:
        return self.models[self.get_default_model_id()]

    def get_available_models(self) -> Dict[str, Model]:
        return self.models

    def init(self) -> Any:
        return self.get_api()

    def set_spending_estimator(self, estimator: SpendingEstimator):
        self.spending_estimator = estimator

    def send_prompt(self, model_id: str, prompt: str) -> RequestResult:
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found for {self.__class__.__name__}")

        if self.spending_estimator is None:
            raise ValueError(f"SpendingEstimator is not set")

        # Before sending the prompt, estimate current spending
        self.spending_estimator.control_spending(strict=True)

        model = self.models[model_id]
        result = self._send_prompt(model, prompt)
        
        # Estimate the cost
        model.update_usage(result.usage)

        return result

    def estimate_spending(self) -> float:
        spending = 0
        for model in self.models.values():
            spending += model.estimate_spending()
        return spending

    @abstractmethod
    def _send_prompt(self, model: Model, prompt: str) -> RequestResult:
        """Sends a prompt to the API and returns the result."""
        pass

    def _add_model(self, model: Model):
        self.models[model.id] = model

    def _add_models(self, models: Dict[str, Model]):
        self.models.update(models)

    def _build_model_dict(self, models: List[type[Model]]) -> Dict[str, Model]:
        for model_class in models:
            model = model_class()
            self.models[model.id] = model

    def _get_api_key(self) -> str:
        """Retrieves the API key securely."""
        # Try environment variables first
        api_key = os.getenv(self.get_api_key_env_var())
        if api_key:
            return api_key
        
        # Otherwise ask the user
        manager_name = self.get_name()
        print(f"{manager_name} API key not found in environment variables.")
        api_key = getpass.getpass(f"Enter your {manager_name} API key: ")
        return api_key
