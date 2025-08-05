# coding: utf-8

import argparse
import datetime
import json
import logging
import pandas as pd
import pathlib

"""
https://github.com/dataforgoodfr/offseason-shelter-for-science/issues/76
"""

from sqlalchemy.orm import load_only
from sqlalchemy.sql import func

from rescue_db.rescue_api import database
from rescue_db.rescue_api.models import Dataset, DatasetRank

logging.basicConfig(level=logging.INFO)

DEFAULT_OUTPUT_DIR = "/data/analyze"

argparser = argparse.ArgumentParser()
argparser.add_argument(
    "organizations_path", type=pathlib.Path, help="Path to the organizations CSV file"
)
argparser.add_argument(
    "--output-dir",
    type=pathlib.Path,
    default=DEFAULT_OUTPUT_DIR,
)
argparser.add_argument(
    "--ranking-ids",
    nargs="+",
    default=[8, 9],
    help="List of ranking IDs to consider for the analysis. Event count will be summed for these IDs when dataset are encountered multiple times.",
)

args = argparser.parse_args()

args.output_dir = args.output_dir.resolve(strict=True)
if not args.output_dir.is_dir():
    args.output_dir.mkdir(parents=True, exist_ok=True)

file_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

organizations = (
    pd.read_csv(args.organizations_path, encoding="utf-8")
    .set_index("id")[["dg_name", "dg_title", "description", "keywords"]]
    .to_dict("index")
)

db = next(database.get_db())

# ** BUILD SUBQUERY FOR MOST POPULAR DATASETS **
# SELECT d.id AS dataset_id, SUM(event_count) AS popularity_score
# FROM public.datasets d
# INNER JOIN public.dataset_ranks dr ON dr.dataset_id=d.id
# WHERE d.access_direct_dl_count=d.access_total_count
# GROUP BY d.id;
most_popular_datasets_subquery = (
    db.query(Dataset, func.sum(DatasetRank.event_count).label("popularity_score"))
    .filter(Dataset.access_direct_dl_count == Dataset.access_total_count)
    .join(DatasetRank, Dataset.id == DatasetRank.dataset_id)
    .filter(DatasetRank.ranking_id.in_(args.ranking_ids))
    .options(load_only(Dataset.id))
    .group_by(Dataset.id)
    .subquery()
)
# ** GET MOST POPULAR DATASETS WITH THE HELP OF THE SUBQUERY **
most_popular_datasets = (
    db.query(Dataset)
    .join(
        most_popular_datasets_subquery,
        Dataset.id == most_popular_datasets_subquery.c.id,
    )
    .options(
        load_only(
            Dataset.id,
            Dataset.dg_id,
            Dataset.dg_name,
            Dataset.dg_title,
            Dataset.dg_notes,
            Dataset.organization_id,
        )
    )
    .all()
)

output_dicts = {}

for dataset in most_popular_datasets:
    org = organizations.get(dataset.organization_id)
    if not org:
        raise ValueError(
            f"Organization with ID {dataset.organization_id} not found in the provided CSV file."
        )

    org_name = org.get("dg_name")
    if not org_name in output_dicts:
        output_dicts[org_name] = {
            "title": org.get("dg_title"),
            "description": org.get("description", ""),
            "keywords": org.get("keywords").split(","),
            "datasets": {"count": 0, "items": []},
        }
    output_dicts[org_name]["datasets"]["items"].append(
        {
            "id": dataset.id,
            "dg_id": dataset.dg_id,
            "dg_name": dataset.dg_name,
            "dg_title": dataset.dg_title,
            "dg_notes": dataset.dg_notes,
        }
    )

for org_name, org_data in output_dicts.items():
    output_dicts[org_name]["datasets"]["count"] = len(org_data["datasets"]["items"])

with open(
    args.output_dir / f"most_popular_datasets_{file_datetime}.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(output_dicts, f, ensure_ascii=False, indent=4)
