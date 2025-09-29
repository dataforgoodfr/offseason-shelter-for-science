# coding: utf-8

from ai.api.model import Model
from ai.api.manager import APIManagerInterface, get_instance as get_manager_instance, get_instances as get_manager_instances

class SpendingEstimator:
    __instance = None

    @classmethod
    def create_instance(cls, limit: float) -> "SpendingEstimator":
        if cls.__instance is not None:
            raise ValueError("SpendingEstimator already created")

        cls.__instance = cls(limit)

        return cls.__instance

    @classmethod
    def get_instance(cls, create_if_none=False) -> "SpendingEstimator":
        if cls.__instance is None:
            if not create_if_none:
               raise ValueError("SpendingEstimator not created")
            else:
                cls.create_instance()

        return cls.__instance

    def __init__(self, limit: float):
        self.limit = limit

    def estimate_api_spending(self, api: str | APIManagerInterface) -> float:
        """Estimate API current spending"""

        # Load the API manager
        if isinstance(api, str):
            api_manager = get_manager_instance(api)
        else:
            api_manager = api

        return api_manager.estimate_spending()

    def estimate_model_cost(self, api: str | APIManagerInterface, model: str | Model) -> float:
        """Estimate model current spending"""

        # Load the API manager
        if isinstance(api, str):
            api_manager = get_manager_instance(api)
        else:
            api_manager = api
        if isinstance(model, str):
            model = api_manager.models[model]

        return model.estimate_spending()

    def estimate_spending(self) -> float:
        """Estimate current spending for all APIs and models"""

        spending = 0
        for api in get_manager_instances():
            spending += self.estimate_api_spending(api)

        return spending

    def control_spending(self, strict: bool, display: bool=False) -> bool:
        """Control current spending for all APIs and models"""

        spending = self.estimate_spending()
        if display:
            print(f"Total spending: {spending}")
        if spending > self.limit:
            if strict:
                raise ValueError(f"Current spending is {spending}, limit is {self.limit}, please wait for the next month")
            else:
                return False

        return True