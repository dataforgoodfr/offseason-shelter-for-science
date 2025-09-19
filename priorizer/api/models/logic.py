# coding: utf-8

import pathlib

from rescue_api.models.dataset_rank import DatasetRank
from rescue_api.models.resource import Resource
from rescue_api.models.asset import Asset
from rescue_api.models.asset_resource import asset_resource
from rescue_api.models.mvp_downloader_library import MvpDownloaderLibrary
from rescue_api.database import get_db
from sqlalchemy import func, case, desc, and_
from datetime import datetime, timezone
from typing import List

_RANKING_LIMIT = 100



class RankedRequestManager:
    def __init__(self):
        pass

    def get_rank(self) -> dict:
        session = next(get_db())

        # Return latest rank update 
        sub_query = (session.query(DatasetRank.dataset_id, func.max(DatasetRank.updated_at).label("max_updated_at")).group_by(DatasetRank.dataset_id).subquery())

        # Fetch dataset last ranking info accross mvp_downloader_library, dataset_rank and resource table 
        ranks = (
                session.query(
                        MvpDownloaderLibrary.dataset_id,
                        MvpDownloaderLibrary.resource_id,
                        MvpDownloaderLibrary.deeplink,
                        MvpDownloaderLibrary.deeplink_file_size,
                        MvpDownloaderLibrary.magnet_link,
                        DatasetRank.event_count,
                        DatasetRank.updated_at,
                        DatasetRank.rank,
                        asset_resource.c.asset_id,
                )
                .join(DatasetRank, DatasetRank.dataset_id == MvpDownloaderLibrary.dataset_id)
                .join(Resource, Resource.id == MvpDownloaderLibrary.resource_id)
                .join(sub_query, (DatasetRank.dataset_id == sub_query.c.dataset_id) & (DatasetRank.updated_at == sub_query.c.max_updated_at))
                .join(asset_resource, asset_resource.c.resource_id == MvpDownloaderLibrary.resource_id)
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
                "url": r.magnet_link if r.magnet_link else r.deeplink
                }
                for r in ranks]
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
        
