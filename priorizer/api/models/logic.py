# coding: utf-8

import pathlib

from rescue_api.models.dataset_rank import DatasetRank
from rescue_api.models.resource import Resource
from rescue_api.models.asset import Asset
from rescue_api.models.asset_resource import asset_resource
from rescue_api.models.mvp_downloader_library import MvpDownloaderLibrary
from rescue_api.database import get_db
from sqlalchemy import func, case, desc
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

        
        latest_updated = (
                session.query(
                        Rank.dataset_id,
                        func.max(Rank.updated_at).label("max_updated_at")
                        )
                        .group_by(Rank.dataset_id)
                        .subquery()
                )
        # List last updated ranks for each dataset_id
        latest_ranks = (
                session.query(
                Rank.dataset_id,
                Rank.rank,
                Rank.updated_at
                )
                .join(
                latest_updated,
                and_(
                        Rank.dataset_id == latest_updated.c.dataset_id,
                        Rank.updated_at == latest_updated.c.max_updated_at
                )
                )
                .subquery()
        )

        min_rank_per_dataset = (
                session.query(
                latest_ranks.c.dataset_id,
                func.min(latest_ranks.c.rank).label("min_rank")
                )
                .group_by(latest_ranks.c.dataset_id)
                .subquery()
        )

        results = (
                session.query(
                latest_ranks.c.dataset_id,
                latest_ranks.c.updated_at,
                min_rank_per_dataset.c.min_rank
                )
                .join(
                min_rank_per_dataset,
                and_(
                        latest_ranks.c.dataset_id == min_rank_per_dataset.c.dataset_id,
                        latest_ranks.c.rank == min_rank_per_dataset.c.min_rank
                )
                )
                .all()
        )
        # First rank never rescued assets (=with no magnet link), the more events there are the higher the rank is
        # Apply same methodology to assets with magnet_link 
        ranks = (
                session.query(
                        MvpDownloaderLibrary.magnet_link,
                        DatasetRank.dataset_id,
                        DatasetRank.event_count,
                        DatasetRank.updated_at,
                        DatasetRank.rank
                )
                .join(DatasetRank, DatasetRank.dataset_id == MvpDownloaderLibrary.dataset_id)
                .join(sub_query, (DatasetRank.dataset_id == sub_query.c.dataset_id) & (DatasetRank.updated_at == sub_query.c.max_updated_at))
                .order_by(
                        case((MvpDownloaderLibrary.magnet_link==None, 0), else_=1), 
                        desc(DatasetRank.event_count)
                )
                .all()
        )

        row_count = session.query(func.count(DatasetRank.id)).scalar()

        # Keep same update time for whole new ranks
        update_ts = datetime.now(timezone.utc)
        results = [{
                "dataset_id": str(r.dataset_id),
                "ranking_id": update_ts.strftime("%Y%m%d"),
                "event_count": r.event_count,
                "db_rank": r.rank,
                "rank": idx + 1,
                "url": r.magnet_link,
                "updated_at": r.updated_at
                }
                for idx, r in enumerate(ranks)]        
        
        # Only return amended ranks
        fil_results = [{
                "id": row_count + idx + 1,
                "dataset_id": r["dataset_id"],
                "ranking_id": r["ranking_id"],
                "event_count": r["event_count"],
                "db_rank": r["db_rank"],
                "updated": r["updated_at"],
                "rank": r["rank"]
        } for idx, r in enumerate(results) if r["db_rank"] != r["rank"]]

        return fil_results