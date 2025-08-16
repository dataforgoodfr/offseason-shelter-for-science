import atexit
import logging

#from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from fastapi import FastAPI
from models.state import app_state
from routers import dispatch

# App configuration
app = FastAPI()
app.include_router(dispatch.router)
