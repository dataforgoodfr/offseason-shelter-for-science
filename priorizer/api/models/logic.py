# coding: utf-8

import logging

from rescue_api.models.dataset_rank import DatasetRank
from rescue_api.models.dataset_ranking import DatasetRanking
from rescue_api.models.resource import Resource
from rescue_api.models.asset import Asset
from rescue_api.models.asset_resource import asset_resource
from rescue_api.models.mvp_downloader_library import MvpDownloaderLibrary
from rescue_api.models.rescues import Rescue
from rescue_api.database import get_db
from sqlalchemy import func, case, desc, and_
from datetime import datetime, timezone
from typing import List

_RANKING_LIMIT = 100
_MVP_RANKING_ID = 8 # broija 2025-09-20 : MVP default ranking id

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ComputeRankResult:
    def __init__(self, ranking_id: int, ranking_date: datetime, new_ranks: List[DatasetRank], is_new_ranking: bool):
        self.ranking_id = ranking_id
        self.ranking_date = ranking_date
        self.new_ranks = new_ranks
        self.is_new_ranking = is_new_ranking

class RankedRequestManager:
    def __init__(self):
        pass

    # Retrieve last ranking id : default or auto
    def _get_last_ranking_id(self) -> int:
        session = next(get_db())
        last_ranking_id = session.query(func.max(DatasetRanking.id)).where(DatasetRanking.type == "auto").scalar()
        if not last_ranking_id:
            last_ranking_id = _MVP_RANKING_ID
        
        logger.info(f"Last ranking id: {last_ranking_id}")
        return last_ranking_id

    def _write_query(self, query):
        statement = str(query.statement)
        print(statement)
        import pathlib
        no_magnet_rank_sql_file = pathlib.Path(__file__).parent.parent / "data" / "queries.sql"
        with open(no_magnet_rank_sql_file, "a") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S:") + "\n")
            f.write(statement + "\n")

    def get_rank(self) -> dict:
        session = next(get_db())

        # Get max ranking id
        last_ranking_id = self._get_last_ranking_id()

        # Fetch deeplinks from mvp_downloader_library that are not rescued yet
        no_magnet_ranks = (
                session.query(
                        MvpDownloaderLibrary.dataset_id,
                        MvpDownloaderLibrary.resource_id,
                        MvpDownloaderLibrary.deeplink,
                        MvpDownloaderLibrary.deeplink_file_size,
                        # No need to retrieve event_count
                        # No need to retrieve updated_at
                        DatasetRank.rank,
                        asset_resource.c.asset_id
                )
                .join(DatasetRank, DatasetRank.dataset_id == MvpDownloaderLibrary.dataset_id)
                .join(Resource, Resource.id == MvpDownloaderLibrary.resource_id)
                .join(asset_resource, asset_resource.c.resource_id == MvpDownloaderLibrary.resource_id)
                .outerjoin(Rescue, Rescue.asset_id == asset_resource.c.asset_id)
                .where(DatasetRank.ranking_id == last_ranking_id).where(Rescue.asset_id.is_(None))
                .order_by(DatasetRank.rank, Resource.id)
                .limit(_RANKING_LIMIT)
        )

        results = [{
                "path": "",
                "name": "",
                "priority": r.rank,
                "size_mb": r.deeplink_file_size,
                "ds_id": r.dataset_id,
                "res_id": r.resource_id,
                "asset_id": r.asset_id,
                "url": r.deeplink
                }
                for r in no_magnet_ranks]

        # If not enough results, complete with results with magnet link
        if len(results) < _RANKING_LIMIT:
                magnet_ranks = (
                        session.query(
                                MvpDownloaderLibrary.dataset_id,
                                MvpDownloaderLibrary.resource_id,
                                MvpDownloaderLibrary.deeplink_file_size,
                                DatasetRank.rank,
                                asset_resource.c.asset_id,
                                Rescue.magnet_link
                        )
                        .join(DatasetRank, DatasetRank.dataset_id == MvpDownloaderLibrary.dataset_id)
                        .join(Resource, Resource.id == MvpDownloaderLibrary.resource_id)
                        .join(asset_resource, asset_resource.c.resource_id == MvpDownloaderLibrary.resource_id)
                        .outerjoin(Rescue, Rescue.asset_id == asset_resource.c.asset_id)
                        .where(DatasetRank.ranking_id == last_ranking_id)
                        .where(Rescue.asset_id.is_not_(None))
                        .order_by(DatasetRank.rank, Resource.id)
                        .limit(_RANKING_LIMIT)
                )
                while len(results) < _RANKING_LIMIT:
                        for r in magnet_ranks:
                                results.append({
                                        "path": "",
                                        "name": "",
                                        "priority": r.rank,
                                        "size_mb": r.deeplink_file_size,
                                        "ds_id": r.dataset_id,
                                        "res_id": r.resource_id,
                                        "asset_id": r.asset_id,
                                        "url": r.magnet_link
                                })
        return {"assets": results}
        
    def compute_rank(self) -> List[dict]:
        session = next(get_db())

        # List last rank timestamp by dataset_id
        latest_updated = (
                session.query(
                        DatasetRank.dataset_id,
                        func.min(DatasetRank.rank).label("rank"),
                        func.max(DatasetRank.event_count).label("event_count"),                      
                        func.max(DatasetRank.updated_at).label("updated_at")
                        )
                        .group_by(DatasetRank.dataset_id)
                        .subquery()
                )
        # Magnets are at resource_id level, dataset won't be considered as completed until all resource have their magnet. mvp table is at resource level and can have duplicates in datasets.
        # Could be useful to create a model dataset/completed to ensure all dataset's resources have their magnet.
        ds_magnets = (
                session.query(
                        MvpDownloaderLibrary.dataset_id,
                        func.count(MvpDownloaderLibrary.resource_id).label("nb_resources"),
                        func.sum(
                                case(
                                        (MvpDownloaderLibrary.magnet_link==None, 0),
                                        else_=1
                                        )
                                ).label("nb_magnets")
                        )
                        .group_by(MvpDownloaderLibrary.dataset_id)
                .subquery()
        )
        
        ds_completion_status = (
                session.query(
                        ds_magnets.c.dataset_id,
                        case((ds_magnets.c.nb_magnets==ds_magnets.c.nb_resources, True), else_=False).label("completed")
                ).subquery()
        )
        # First rank never rescued assets (=with no magnet link), the more events there are the higher the rank is
        # Apply same methodology to assets with magnet_link 
        ranks = (
                session.query(
                        ds_completion_status.c.completed,
                        latest_updated.c.dataset_id,
                        latest_updated.c.event_count,
                        latest_updated.c.updated_at,
                        latest_updated.c.rank
                )
                .join(
                        latest_updated, 
                        latest_updated.c.dataset_id == ds_completion_status.c.dataset_id
                )
                .order_by(
                        case((ds_completion_status.c.completed==False, 0), else_=1), 
                        desc(latest_updated.c.event_count)
                )
                .all()
        )

        # Keep same update time for whole new ranks
        update_ts = datetime.now(timezone.utc)
        results = [{
                "dataset_id": str(r.dataset_id),
                "ranking_id": update_ts.strftime("%Y%m%d"),
                "event_count": r.event_count,
                "db_rank": r.rank,
                "rank": idx + 1,
                "updated_at": r.updated_at
                }
                for idx, r in enumerate(ranks)]

        last_idx = session.query(func.max(DatasetRank.id)).scalar()
        # Only return amended ranks
        fil_results = [{
                "id": last_idx + idx + 1,
                "dataset_id": r["dataset_id"],
                "ranking_id": r["ranking_id"],
                "event_count": r["event_count"],
                "db_rank": r["db_rank"],
                "updated": r["updated_at"],
                "rank": r["rank"]
        } for idx, r in enumerate(results) if r["db_rank"] != r["rank"]]
        return fil_results
        
