# coding: utf-8

import argparse
import datetime
import logging
import pandas as pd
import pathlib

from sqlalchemy.orm import load_only

from rescue_db.rescue_api import database
from rescue_db.rescue_api.models import Organization

logging.basicConfig(level=logging.INFO)

DEFAULT_OUTPUT_DIR = "/data/analyze"

argparser = argparse.ArgumentParser()
argparser.add_argument(
    "--output-dir",
    type=pathlib.Path,
    default=DEFAULT_OUTPUT_DIR,
)

args = argparser.parse_args()

args.output_dir = args.output_dir.resolve(strict=True)
if not args.output_dir.is_dir():
    args.output_dir.mkdir(parents=True, exist_ok=True)

file_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

db = next(database.get_db())
org_res = (
    db.query(Organization)
    .options(load_only(Organization.id, Organization.dg_name, Organization.dg_title))
    .all()
)
org_df = pd.DataFrame(
    [
        {
            "id": org.id,
            "dg_name": org.dg_name,
            "dg_title": org.dg_title,
        }
        for org in org_res
    ]
)
org_df.to_csv(args.output_dir / f"organizations_{file_datetime}.csv", index=False)

# @todo : Enrich the CSV with AI :
# Prompt :
# For each agency, can you provide :
# - a column describing it in a few words
# - another column with keywords to facilitate a potential search