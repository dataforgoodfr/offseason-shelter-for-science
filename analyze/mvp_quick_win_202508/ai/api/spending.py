# coding: utf-8

from ai.api.model import Model
from ai.api.manager import APIManagerInterface, create_manager, create_managers

class SpendingEstimator:
    __instance = None

    @classmethod
    def create_estimator(cls, limit: float) -> "SpendingEstimator":
        if cls.__instance is not None:
            raise ValueError("SpendingEstimator already created")

        cls.__instance = cls(limit)

        return cls.__instance

    @classmethod
    def get_instance(cls) -> "SpendingEstimator":
        if cls.__instance is None:
            raise ValueError("SpendingEstimator not created")

        return cls.__instance

    def __init__(self, limit: float):
        self.limit = limit

    def estimate_api_cost(self, api: str | APIManagerInterface) -> float:
        """Estimate API current spending"""

        # Load the API manager
        if isinstance(api, str):
            api_manager = create_manager(api)
        else:
            api_manager = api

        return api_manager.estimate_spending()

    def estimate_model_cost(self, api: str | APIManagerInterface, model: str | Model) -> float:
        """Estimate model current spending"""

        # Load the API manager
        if isinstance(api, str):
            api_manager = create_manager(api)
        else:
            api_manager = api
        if isinstance(model, str):
            model = api_manager.models[model]

        return model.estimate_spending()

    def estimate_spending(self) -> float:
        """Estimate current spending for all APIs and models"""

        spending = 0
        for api in create_managers():
            spending += self.estimate_api_cost(api)

        return spending

    def control_spending(self, strict: bool) -> bool:
        """Control current spending for all APIs and models"""

        spending = self.estimate_spending()
        if spending > self.limit:
            if strict:
                raise ValueError(f"Current spending is {spending}, limit is {self.limit}, please wait for the next month")
            else:
                return False

        return True