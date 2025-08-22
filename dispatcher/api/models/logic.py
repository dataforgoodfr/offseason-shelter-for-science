import json
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime  # Import spécifique de la classe datetime
import logging
import uuid

from .payload import AssetModel

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Dispatcher:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.ranker_file = self.data_dir / "ranker_mock.json"
        self.alloc_file = self.data_dir / "allocations.json"
        self.rescues_file = self.data_dir / "rescues_mock.json"

        self._init_files()
    
    def _init_files(self):
        """Crée les fichiers s'ils n'existent pas avec un contenu valide"""
        self.data_dir.mkdir(exist_ok=True)
        
        # Fichier ranker
        if not self.ranker_file.exists() or self.ranker_file.stat().st_size == 0:
            self.ranker_file.write_text(
                json.dumps([
                    {
                        "ds_id": "1e5add2c-88db-4a35-b23d-289db927f57a",
                        "res_id": "907ca678-6428-4dca-9022-ec4dee9f8e37",
                        "asset_id": "45445",
                        "path": "data_gov_ca-gov_20250601_120256/package_search_S0000.json",
                        "name": "CHHS CA mock data 1",
                        "size_mb": 4.5,
                        "priority": 1,
                        "url": "https://data.chhs.ca.gov/dataset/5a281abf-1730-43b0-b17b-ac6a35db5760/resource/724c6fd8-a645-4e52-b63f-32631a20db5d/download/adult-depression-lghc-indicator-24.csv"
                    },
                    {
                        "ds_id": "1e5add2c-88db-4a35-b23d-289db927f57a",
                        "res_id": "198759ae-9144-49be-bff2-f2089e33270b",
                        "asset_id": "15625",
                        "path": "data_gov_ca-gov_20250601_120256/package_search_S0000.json",
                        "name": "CHHS CA mock data 2",
                        "size_mb": 16.2,
                        "priority": 1,
                        "url": "https://data.cdc.gov/api/views/bi63-dtpu/rows.csv?accessType=DOWNLOAD"
                    },
                    {
                        "ds_id": "d3",
                        "res_id": "54898dz0-4485-4sq1-szzd-f891d32ss1546",
                        "asset_id": "71465",
                        "path": "data_gov_ca-gov_20250601_120256/package_search_S0000.json",
                        "name": "Dataset 3",
                        "size_mb": 156,
                        "priority": 6,
                        "url": "magnet:?xt=urn:btih:dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c&dn=Big+Buck+Bunny&tr=udp%3A%2F%2Fexplodie.org%3A6969&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Ftracker.empire-js.us%3A1337&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=wss%3A%2F%2Ftracker.btorrent.xyz&tr=wss%3A%2F%2Ftracker.fastcast.nz&tr=wss%3A%2F%2Ftracker.openwebtorrent.com&ws=https%3A%2F%2Fwebtorrent.io%2Ftorrents%2F&xs=https%3A%2F%2Fwebtorrent.io%2Ftorrents%2Fbig-buck-bunny.torrent"
                    }
                ])
            )
        
        # Fichier d'allocations
        if not self.alloc_file.exists() or self.alloc_file.stat().st_size == 0:
            self.alloc_file.write_text(json.dumps([]))

        # File with rescues
        if not self.rescues_file.exists() or self.rescues_file.stat().st_size == 0:
            self.rescues_file.write_text(
                json.dumps([
                    {
                        "asset_id": 71465,
                        "rescuer_id": 154562,
                        "magnet_link": "magnet:?xt=urn:btih:d3",
                        "status": "FAIL"
                    },
                    {
                        "asset_id": 69532,
                        "rescuer_id": 198574,
                        "magnet_link": "magnet:?xt=urn:btih:d1",
                        "status": "SUCCESS"
                    }
                ])
            )

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

    @staticmethod
    def _save_json(file: Path, data: List[Dict]):
        file.write_text(json.dumps(data, indent=2))
    
    def get_available_assets(self) -> List[Dict]:   
        """Récupère tous les assets (sans filtrage par allocation)"""
        return self._load_json(self.ranker_file)
           
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
        # TODO - not MVP: Enhance allocation logs with rescuer_id + allocation status
        allocations = self._load_json(self.alloc_file)
        new_entries = [{
            "ds_id": a['ds_id'],
            "res_id": a['res_id'],
            "asset_id": a['asset_id'],
            "name": a['name'],
            "size_mb": float(a['size_mb']),
            "priority": int(a['priority']),
            "url": a['url']
        } for a in selected]

        
        self._save_json(self.alloc_file, allocations + new_entries)

        return {
            "node_id": node_id,
            "allocated_size_mb": sum(a['size_mb'] for a in selected),
            "assets": selected,
            "allocation_id": str(uuid.uuid4())
        }

    def update_rescues_in_db(self, rescuer_id: int, assets: List[AssetModel]) -> Dict:
        print("Inside 'update_rescues_in_db'")

        rescues_from_db = self._load_json(self.rescues_file)
        downloaded_asset_ids = [int(asset.asset_id) for asset in assets]

        rescues_to_update = [
            rescue
            for rescue in rescues_from_db
            if rescue["rescuer_id"] == rescuer_id and rescue["asset_id"] in downloaded_asset_ids
        ]

        rescues_not_to_update = [rescue for rescue in rescues_from_db if rescue not in rescues_to_update]
        updated_rescues = self._update_rescues(rescues=rescues_to_update, assets=assets)
        print(f"Updated rescues: {updated_rescues}")
        rescues = rescues_not_to_update + updated_rescues
        print(f"New rescues: {rescues}")

        try:
            self._save_json(self.rescues_file, rescues_not_to_update + updated_rescues)
        except Exception as e:
            print(e)
            return {
                "action": "Update magnet link and status of rescues",
                "rescuer_id": rescuer_id,
                "asset_ids": downloaded_asset_ids,
                "action_status": "FAIL",
            }
        else:
            return {
                "action": "Update magnet link and status of rescues",
                "rescuer_id": rescuer_id,
                "asset_ids": downloaded_asset_ids,
                "action_status": "SUCCESS",
            }


    @staticmethod
    def _get_filtered_rescues(rescuer_id: int, asset_ids: List[int]) -> List[Dict]:
        print("Inside '_get_filtered_rescues'")

        filtered_rescues = [rescue for rescue in all_rescues if rescue["rescuer_id"] == rescuer_id]
        return [rescue for rescue in filtered_rescues if rescue["asset_id"] in asset_ids]

    def _update_rescues(self, rescues: List[Dict], assets: List[AssetModel]) -> List[Dict]:
        print("Inside '_update_rescues'")

        updated_rescues = []
        for rescue in rescues:
            asset = self._find_corresponding_asset(asset_id=rescue["asset_id"], assets=assets)
            rescue["magnet_link"] = asset.magnet_link
            rescue["status"] = asset.status.value
            updated_rescues.append(rescue)

        return updated_rescues

    @staticmethod
    def _find_corresponding_asset(asset_id: int, assets: List[AssetModel]) -> AssetModel:
        print("Inside '_find_corresponding_asset'")

        for asset in assets:
            print(f"asset.asset_id={asset.asset_id}")
            print(f"Type of asset.asset_id={type(asset.asset_id)}")
            if asset_id == int(asset.asset_id):
                print("Inside if statement")
                return asset

        raise ValueError(
            f"The asset from the database with the ID={asset_id} couldn't be matched "
            f"with the ones provided by the app."
        )
