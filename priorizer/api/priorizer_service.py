import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from fastapi import FastAPI
from models.state import app_state
from routers import priorizer

# App configuration
app = FastAPI()
app.include_router(priorizer.router)

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialisation du scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def priority_update():
    pass
#    """Tâche planifiée avec gestion d'erreur améliorée"""
#    try:
#        logger.info("Début de la mise à jour automatique...")
#        
#        # Vérification des fichiers
#        #if not dispatcher.ckan_file.exists():
#        #    dispatcher._init_files()
#            
#        # 1. Chargement avec nouvelle méthode robuste
#        #allocations = dispatcher._load_json(dispatcher.alloc_file)
#        #ckan_data = dispatcher._load_json(dispatcher.ckan_file)
#        
#        if not ckan_data:
#            logger.error("Aucune donnée CKAN valide trouvée")
#            return
#            
#        # 2. Nettoyage des allocations
#        updated_allocations = [
#            alloc for alloc in allocations 
#            if alloc.get('status') != 'ALLOCATED' or 
#            (datetime.now() - datetime.fromisoformat(alloc.get('timestamp', '2000-01-01'))) < timedelta(hours=24)
#        ]
#        
#        # 3. Mise à jour des priorités
#        for dataset in ckan_data:
#            if isinstance(dataset, dict):  # Validation supplémentaire
#                dataset['priority'] = max(1, min(10, dataset.get('priority', 5) + random.randint(-1, 1)))
#        
#        # Sauvegarde
#        #dispatcher._save_json(dispatcher.alloc_file, updated_allocations)
#        #dispatcher._save_json(dispatcher.ckan_file, ckan_data)
#        
#        logger.info("Mise à jour automatique terminée avec succès")
#        
#    except Exception as e:
#        logger.error(f"Échec critique de la mise à jour automatique: {str(e)}", exc_info=True)

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


#@app.post("/update-ckan")
#async def update_ckan_data(request: CkanUpdateRequest):
#    """Endpoint manuel pour forcer la mise à jour des données CKAN"""
#    try:
#        ckan_data = dispatcher._load_json(dispatcher.ckan_file)
#        
#        # Mise à jour des priorités selon la requête
#        for update in request.updates:
#            for dataset in ckan_data:
#                if dataset['id'] == update.asset_id:
#                    dataset['priority'] = update.new_priority
#                    break
#        
#        dispatcher._save_json(dispatcher.ckan_file, ckan_data)
#        return {"status": "success", "updated_items": len(request.updates)}
#    
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))
