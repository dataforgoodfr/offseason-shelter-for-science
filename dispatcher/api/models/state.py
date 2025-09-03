"""
Global state manager for the dispatcher service application.
"""

import logging
import os

from typing import Optional
from models.logic import Dispatcher
from models.priorizer_client import PriorizerClient


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
        
        # Priorizer client configuration
        priorizer_url = os.getenv('PRIORIZER_URL', 'http://priorizer-api:8082')
        priorizer_client = PriorizerClient(base_url=priorizer_url)
        
        # Dispatcher configuration with priorizer client
        self._dispatcher: Dispatcher = Dispatcher(priorizer_client=priorizer_client)


# Global state instance
app_state = AppState()