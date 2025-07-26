from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from dispatcher.schemas import DispatchRequest, ReleaseRequest, AssetResponse, CkanUpdateRequest
from dispatcher.logic import Dispatcher
import uuid
from typing import List
import atexit
from datetime import datetime, timedelta
import logging
import random


# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI()
dispatcher = Dispatcher()

# Initialisation du scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def auto_priority_update():
    """Tâche planifiée avec gestion d'erreur améliorée"""
    try:
        logger.info("Début de la mise à jour automatique...")
        
        # Vérification des fichiers
        if not dispatcher.ckan_file.exists():
            dispatcher._init_files()
            
        # 1. Chargement avec nouvelle méthode robuste
        allocations = dispatcher._load_json(dispatcher.alloc_file)
        ckan_data = dispatcher._load_json(dispatcher.ckan_file)
        
        if not ckan_data:
            logger.error("Aucune donnée CKAN valide trouvée")
            return
            
        # 2. Nettoyage des allocations
        updated_allocations = [
            alloc for alloc in allocations 
            if alloc.get('status') != 'ALLOCATED' or 
            (datetime.now() - datetime.fromisoformat(alloc.get('timestamp', '2000-01-01'))) < timedelta(hours=24)
        ]
        
        # 3. Mise à jour des priorités
        for dataset in ckan_data:
            if isinstance(dataset, dict):  # Validation supplémentaire
                dataset['priority'] = max(1, min(10, dataset.get('priority', 5) + random.randint(-1, 1)))
        
        # Sauvegarde
        dispatcher._save_json(dispatcher.alloc_file, updated_allocations)
        dispatcher._save_json(dispatcher.ckan_file, ckan_data)
        
        logger.info("Mise à jour automatique terminée avec succès")
        
    except Exception as e:
        logger.error(f"Échec critique de la mise à jour automatique: {str(e)}", exc_info=True)

@app.on_event("startup")
def init_scheduler():
    """Initialise le scheduler au démarrage"""
    # Tâche toutes les 10 minutes
    scheduler.add_job(
        auto_priority_update,
        'interval',
        minutes=2,
        next_run_time=datetime.now()  # Exécution immédiate au démarrage
    )

@app.post("/allocate", response_model=List[AssetResponse])
async def allocate_assets(request: DispatchRequest):
    result = dispatcher.allocate_assets(
        free_space_mb=request.free_space_gb * 1024,
        node_id=request.node_id
    )
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No available assets matching the criteria"
        )
    
    # Conversion des champs pour correspondre à AssetResponse
    formatted_assets = []
    for asset in result['assets']:
        formatted_assets.append({
            "id": asset["id"],
            "url": asset["url"],  # ou asset.get("download_url") selon votre structure
            "size_mb": asset["size_mb"],
            "priority": asset["priority"],
            "name": asset.get("name", "")  # Champ optionnel
        })
    
    return [AssetResponse(**asset) for asset in formatted_assets]

@app.post("/release")
async def release_asset(request: ReleaseRequest):
    dispatcher.release_assets(
        asset_id=request.asset_id,
        node_id=request.node_id
    )
    return {"status": "success"}

@app.post("/update-ckan")
async def update_ckan_data(request: CkanUpdateRequest):
    """Endpoint manuel pour forcer la mise à jour des données CKAN"""
    try:
        ckan_data = dispatcher._load_json(dispatcher.ckan_file)
        
        # Mise à jour des priorités selon la requête
        for update in request.updates:
            for dataset in ckan_data:
                if dataset['id'] == update.asset_id:
                    dataset['priority'] = update.new_priority
                    break
        
        dispatcher._save_json(dispatcher.ckan_file, ckan_data)
        return {"status": "success", "updated_items": len(request.updates)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def system_status():
    return {
        "ckan_datasets": len(dispatcher._load_json(dispatcher.ckan_file)),
        "active_allocations": len([
            a for a in dispatcher._load_json(dispatcher.alloc_file)
            if a['status'] == "ALLOCATED"
        ]),
        "next_auto_update": str(scheduler.get_jobs()[0].next_run_time)
    }