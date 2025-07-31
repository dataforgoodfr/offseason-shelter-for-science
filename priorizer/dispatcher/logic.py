import json
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime  # Import spécifique de la classe datetime
import logging
import uuid

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Dispatcher:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.ckan_file = self.data_dir / "ckan_mock.json"
        self.alloc_file = self.data_dir / "allocations.json"
        
        self._init_files()
    
    def _init_files(self):
        """Crée les fichiers s'ils n'existent pas avec un contenu valide"""
        self.data_dir.mkdir(exist_ok=True)
        
        # Fichier CKAN
        if not self.ckan_file.exists() or self.ckan_file.stat().st_size == 0:
            self.ckan_file.write_text(json.dumps([
                {"id": "d1", "name": "Dataset 1", "size_mb": 512, "priority": 8, "url": "magnet:?xt=urn:btih:d1"},
                {"id": "d2", "name": "Dataset 2", "size_mb": 256, "priority": 6, "url": "magnet:?xt=urn:btih:d2"}
            ]))
        
        # Fichier d'allocations
        if not self.alloc_file.exists() or self.alloc_file.stat().st_size == 0:
            self.alloc_file.write_text(json.dumps([]))
    
    def _load_json(self, file: Path) -> List[Dict]:
        """Charge un fichier JSON avec gestion robuste des erreurs"""
        try:
            if not file.exists() or file.stat().st_size == 0:
                self._init_files()  # Réinitialise si fichier vide
                return []
                
            content = file.read_text(encoding='utf-8').strip()
            if not content:
                return []
                
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON dans {file.name}: {str(e)}")
            backup_path = file.with_suffix('.bak')
            file.rename(backup_path)
            self._init_files()
            return []
        except Exception as e:
            logger.error(f"Erreur inattendue avec {file.name}: {str(e)}")
            return []
    
    def _save_json(self, file: Path, data: List[Dict]):
        file.write_text(json.dumps(data, indent=2))
    
    def get_available_assets(self) -> List[Dict]:   
        """Récupère tous les assets (sans filtrage par allocation)"""
        return self._load_json(self.ckan_file)
        
    #    return [a for a in ckan_data if a['id'] not in allocated_ids]
    
    def allocate_assets(self, free_space_mb: float, node_id: str = None) -> Dict:
        """Priorise et alloue les assets (version multi-allocation)"""
        available = self.get_available_assets()
        selected = []
        remaining_space = free_space_mb
        
        # Tri par priorité (desc) puis taille (asc)
        for asset in sorted(available, key=lambda x: (-x['priority'], x['size_mb'])):
            if asset['size_mb'] <= remaining_space:
                selected.append(asset)
                remaining_space -= asset['size_mb']
        
        if not selected:
            return None
        
        # Génère un node_id si non fourni
        node_id = node_id or str(uuid.uuid4())
        
        # Enregistrement (on ne vérifie plus les doublons)
        allocations = self._load_json(self.alloc_file)
        new_entries = [{
            "asset_id": a['id'],
            "node_id": node_id,
            "size_mb": a['size_mb'],
            "status": "ALLOCATED",
            "timestamp": datetime.now().isoformat(),
            "allocation_id": str(uuid.uuid4())  # Identifiant unique pour chaque allocation
        } for a in selected]
        
        self._save_json(self.alloc_file, allocations + new_entries)
        
        return {
            "node_id": node_id,
            "allocated_size_mb": sum(a['size_mb'] for a in selected),
            "assets": selected,
            "allocation_ids": [entry['allocation_id'] for entry in new_entries]
        }
    
    def release_assets(self, asset_id: str, node_id: str):
        """Libère un asset alloué"""
        allocations = self._load_json(self.alloc_file)
        
        for alloc in allocations:
            if (alloc['asset_id'] == asset_id and 
                alloc['node_id'] == node_id and
                alloc['status'] == "ALLOCATED"):
                alloc['status'] = "ABORTED"
                alloc['released_at'] = datetime.now().isoformat()
        
        self._save_json(self.alloc_file, allocations)