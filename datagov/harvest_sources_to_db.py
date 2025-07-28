# coding: utf-8

import argparse
import datetime
import json
import logging
import pathlib

from sqlalchemy import text
from sqlalchemy.orm import load_only

from tqdm import tqdm

from rescue_db.rescue_api import database

from rescue_db.rescue_api.models.organization import Organization
from rescue_db.rescue_api.models.dataset import Dataset
from rescue_db.rescue_api.models.harvest_source import (
    HarvestSource,
    HarvestSourceType,
    HarvestFrequency,
    HarvestSourceDataset,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

"""This script processes harvest source metadata file and loads them into a database."""

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
_DATA_DIR = _SCRIPT_DIR.parent.parent.parent / "data"
_LOG_DIR = _DATA_DIR / "log"
DEFAULT_OUTPUT_DIR = _DATA_DIR / "output"

_file_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

argparser = argparse.ArgumentParser()
argparser.add_argument(
    "harvest_file", type=pathlib.Path, help="Path to the harvest source input file"
)
argparser.add_argument(
    "metadata_directory", type=pathlib.Path, help="Directory containing metadata files"
)
# argparser.add_argument("metadata_file_regex", type=str, help="Regex pattern to match metadata files")
argparser.add_argument(
    "--log-level",
    "-L",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
args = argparser.parse_args()

logger.setLevel(args.log_level.upper())

args.harvest_file = args.harvest_file.resolve(strict=True)
metadata_directory = args.metadata_directory.resolve(strict=True)
if not metadata_directory.is_dir():
    logger.error(
        f"Metadata directory {metadata_directory} does not exist or is not a directory."
    )
    exit(1)

# Load harvest source data
harvest_source_data = json.loads(args.harvest_file.read_text(encoding="utf-8"))
logger.info(f"Loaded harvest source data from {args.harvest_file}")


db = next(database.get_db())

# Loading harvest source types
harvest_source_types = {}
results = (
    db.query(HarvestSourceType)
    .options(load_only(HarvestSourceType.id, HarvestSourceType.name))
    .all()
)
for hst in results:
    harvest_source_types[hst.name] = hst.id

# Loading harvest frequencies
harvest_frequencies = {}
results = (
    db.query(HarvestFrequency)
    .options(load_only(HarvestFrequency.id, HarvestFrequency.name))
    .all()
)
for hf in results:
    harvest_frequencies[hf.name] = hf.id

organizations = harvest_source_data["organizations"]

for org_name, organization in organizations.items():
    org_result = (
        db.query(Organization)
        .filter(Organization.dg_name == org_name)
        .options(load_only(Organization.id))
        .one_or_none()
    )
    if not org_result:
        logger.debug(f"Organization {org_name} not found.")
        continue
    org_id = org_result.id
    logger.debug(f"Found organization {org_name} with ID {org_id}")

    # Load harvest sources for the organization
    hs_results = (
        db.query(HarvestSource)
        .filter(HarvestSource.organization_id == org_id)
        .options(load_only(HarvestSource.id, HarvestSource.dg_id))
    )

    db_harvest_sources = {}
    if hs_results:
        db_harvest_sources = {row.dg_id: row.id for row in hs_results}

    json_harvest_sources = organization.get("harvest_sources")

    for json_hs in tqdm(
        json_harvest_sources, desc=f"Processing harvest sources for {org_name}"
    ):
        dg_id = json_hs["id"]

        if dg_id in db_harvest_sources:
            logger.debug(f"Harvest source {dg_id} already exists, skipping.")
            continue

        logger.info(f"Processing harvest source {dg_id} for organization {org_name}")

        harvest_source = HarvestSource()
        harvest_source.dg_id = dg_id
        harvest_source.dg_name = json_hs["name"]
        harvest_source.dg_title = json_hs["title"]
        harvest_source.dg_source = json_hs["source"]
        harvest_source.dg_created = json_hs["created"]
        harvest_source.dg_total_datasets = json_hs["total_datasets"]

        # Associate the harvest source with the organization
        harvest_source.organization_id = org_id

        harvest_source_type_str = json_hs["source_type"]
        if harvest_source_type_str not in harvest_source_types:
            # Create a new harvest source type if it doesn't exist
            harvest_source_type = HarvestSourceType(name=harvest_source_type_str)
            db.add(harvest_source_type)
            db.commit()
            harvest_source_types[harvest_source_type_str] = harvest_source_type.id

        harvest_source.harvest_source_type_id = harvest_source_types[
            harvest_source_type_str
        ]

        harvest_frequency_str = json_hs["freq"]
        if harvest_frequency_str not in harvest_frequencies:
            # Create a new harvest frequency if it doesn't exist
            harvest_frequency = HarvestFrequency(name=harvest_frequency_str)
            db.add(harvest_frequency)
            db.commit()
            harvest_frequencies[harvest_frequency_str] = harvest_frequency.id

        harvest_source.harvest_frequency_id = harvest_frequencies[harvest_frequency_str]
        db_harvest_sources[dg_id] = harvest_source.id

        db.add(harvest_source)

    # Committing harvest sources for the organization
    db.commit()

    # Loadind organization datasets
    logger.info(f"Loading datasets for organization {org_name}")
    dataset_results = (
        db.query(Dataset)
        .filter(Dataset.organization_id == org_id)
        .options(load_only(Dataset.id, Dataset.dg_id))
    )

    db_datasets_dg_id = {}
    db_datasets_id = {}
    for ds in dataset_results:
        ds.harvest_source_id = None  # Initialize harvest_source_id to None

        # Dataset mapping by data.gov ID
        db_datasets_dg_id[ds.dg_id] = ds

        # Dataset mapping by ID
        db_datasets_id[ds.id] = ds

    logger.info(f"Found {len(db_datasets_dg_id)} datasets for organization {org_name}")

    # Loading dataset / harvest source associations
    harvest_source_dataset_results = (
        db.query(HarvestSourceDataset)
        .join(Dataset, HarvestSourceDataset.dataset_id == Dataset.id)
        .filter(Dataset.organization_id == org_id)
        .options(
            load_only(
                HarvestSourceDataset.harvest_source_id, HarvestSourceDataset.dataset_id
            )
        )
    )

    db_harvest_source_datasets = {}
    for hsd in harvest_source_dataset_results:
        # If the dataset exists in db_datasets_id, set the harvest_source_id
        if hsd.dataset_id in db_datasets_id:
            db_datasets_id[hsd.dataset_id].harvest_source_id = hsd.harvest_source_id

        # Create a mapping for quick reference
        db_harvest_source_datasets[hsd.dataset_id] = hsd.harvest_source_id

    logger.info(
        f"Found {len(db_harvest_source_datasets)} harvest source datasets for organization {org_name}"
    )

    metadata_index = 0

    # Load harvest source datasets for the organization
    for metadata_item in metadata_directory.rglob(f"*{org_name}*/*.json"):
        logger.debug(f"Processing metadata file: {metadata_item}")

        datasets = {}

        with metadata_item.open("r", encoding="utf-8") as f:
            metadata = json.load(f)

            if "results" not in metadata:
                logger.warning(f"No results found in metadata file: {metadata_item}")
                continue

            json_datasets = metadata["results"]

            for json_ds in json_datasets:
                ds_dg_id = json_ds.get("id")

                if not ds_dg_id in db_datasets_dg_id:
                    logger.error(
                        f"Dataset {ds_dg_id} not found in database for organization {org_name}"
                    )
                    exit(1)

                harvest_source_dg_id = None
                for extra in json_ds.get("extras", []):
                    if extra.get("key") == "harvest_source_id":
                        harvest_source_dg_id = extra.get("value")
                        break

                # Check if dataset has a harvest source ID
                if (
                    not harvest_source_dg_id
                    or harvest_source_dg_id not in db_harvest_sources
                ):
                    logger.warning(
                        f"Harvest source ID {harvest_source_dg_id} not found for dataset {json_ds.get('id')}"
                    )
                    continue

                # Check if harvest source is known
                if harvest_source_dg_id not in db_harvest_sources:
                    logger.error(f"Harvest source {harvest_source_dg_id} not known")
                    exit(1)

                dataset = db_datasets_dg_id[ds_dg_id]
                if (
                    dataset.harvest_source_id
                    and dataset.harvest_source_id
                    == db_harvest_sources[harvest_source_dg_id]
                ):
                    logger.debug(
                        f"Dataset {ds_dg_id} is already associated with harvest source {harvest_source_dg_id}, skipping."
                    )
                    continue

                hs_ds_association = HarvestSourceDataset(
                    harvest_source_id=db_harvest_sources[harvest_source_dg_id],
                    dataset_id=dataset.id,
                )
                db.add(hs_ds_association)

                db_harvest_source_datasets[dataset.id] = db_harvest_sources[
                    harvest_source_dg_id
                ]

                logger.debug(
                    f"Associated dataset {ds_dg_id} with harvest source {harvest_source_dg_id}"
                )
            logger.info(
                f"Processed {len(json_datasets)} datasets from metadata file {metadata_item}"
            )

            metadata_index += 1
            if metadata_index % 100 == 0:
                logger.info(f"Processed {metadata_index} metadata files so far.")
                db.commit()

        # Committing remaining associations
        if db.dirty:
            db.commit()
