import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from fastapi import FastAPI
from models.state import app_state
from routers import priorizer
from rescue_api.models.dataset_rank import DatasetRank
from rescue_api.database import get_db

# App configuration
app = FastAPI()
app.include_router(priorizer.router)

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialisation du scheduler
scheduler = BackgroundScheduler(daemon=True)
# broija 2025-09-04 : temporary disabling scheduler
# scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def priority_update():
    """Chroned asset priority ranking"""
    try:
        app_state._logger.info("START: Priority ranking update...")        
        updated_ranks = app_state._priorizer.compute_rank()
        app_state._logger.info("SUCCESS: Priority ranking update success")

        app_state._logger.info("Insert new ranking in dataset_ranks table...")
        session = next(get_db())

        session.bulk_insert_mappings(DatasetRank, updated_ranks)
        session.commit()
        session.close()
        app_state._logger.info(f"SUCCESS: {len(updated_ranks)} ranks inserted")
        
    except Exception as e:
        logger.error(f"FAIL: priority ranking update: {str(e)}", exc_info=True)

@app.on_event("startup")
def init_scheduler():
    """Initialise le scheduler au démarrage"""
    # Tâche toutes les 10 minutes
    scheduler.add_job(
        priority_update,
        'interval',
        minutes=2,
        next_run_time=datetime.now()  # Exécution immédiate au démarrage
    )

