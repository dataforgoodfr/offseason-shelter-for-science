"""
Global state manager for the priorizer service application.
"""

import logging

from typing import Optional
from models.logic import RankedRequestManager


class AppState:
    """Singleton state manager to hold global application state."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Logging configuration
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
        self._logger: logging = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        # Priorizer configuration
        self._priorizer: RankedRequestManager = RankedRequestManager()


# Global state instance
app_state = AppState()