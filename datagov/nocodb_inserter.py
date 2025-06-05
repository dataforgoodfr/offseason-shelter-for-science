# coding: utf-8

import argparse
import pathlib
import re

from ckan.package_search import DatasetLoader
from nocodb.api import Manager as APIManager
from nocodb.project import Project

import nocodb.tables

"""
Crawls through directories searching for package_search results, requesting NOCODB API to fill the tables.
"""

URL = "https://noco.services.dataforgood.fr"

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

DEFAULT_DATA_DB_PATH = SCRIPT_DIR.parent / "data/db"
DEFAULT_PROJECT_PATH = DEFAULT_DATA_DB_PATH / "projects.json"
DEFAULT_MAPPING_PATH = DEFAULT_DATA_DB_PATH / "mapping.json"
DEFAULT_PROJECT_NAME = "offseason_us_climate_data_preprod"

argparser = argparse.ArgumentParser()
argparser.add_argument("input", type=pathlib.Path, help="Input directory to crawl in.")
argparser.add_argument(
    "path_regex", help="File path regular expression to filter input files."
)

argparser.add_argument(
    "--project-name", default=DEFAULT_PROJECT_NAME, help="NOCODB project name"
)
argparser.add_argument(
    "--project-path", default=DEFAULT_PROJECT_PATH, help="Path to NOCODB project file."
)
argparser.add_argument(
    "--batch-size",
    default=500,
    help="Call NOCODB API for inserting every X file parsed.",
)

argparser.add_argument(
    "--mapping-path", default=DEFAULT_MAPPING_PATH, help="Path to NOCODB mapping file."
)

args = argparser.parse_args()

args.input = args.input.resolve(strict=True)

api_mgr = APIManager(URL, Project(args.project_path, args.project_name))
api_mgr.load_mapping(args.mapping_path)

# Checking existing organizations in DB.
# @todo : Several scripts running concurrently could lead to organization duplicates
existing_organizations = {}

print("Checking existing organizations...")
api_result = api_mgr.list_records(nocodb.tables.TABLE_DG_ORGANIZATIONS)
if api_result:
    for organization in api_result.list:
        existing_organizations[organization["dg_id"]] = True

path_regex = re.compile(args.path_regex)

loader = DatasetLoader()

datasets = []
resources = []
file_index = 0

# First pass to count items. Not keeping resulting to reduce memory consumption
file_count = len([item for item in args.input.rglob("*.json")])

for item in args.input.rglob("*.json"):
    match_res = path_regex.match(str(item))
    if not match_res:
        continue

    query_result = loader.load(item, resources=True)

    for dataset in query_result.datasets.values():
        # Must insert organization and organization could not be present in NOCODB
        if dataset.organization.id not in existing_organizations:
            result = api_mgr.create_records_from_objects([dataset.organization])
            existing_organizations[dataset.organization.id] = True

        datasets.append(dataset)
        resources += dataset.resources.values()

    file_index += 1

    # Inserting every "batch size" file parsed
    if (file_index % args.batch_size) == 0:
        print(file_index, "/", file_count)

        api_mgr.create_records_from_objects(datasets)
        datasets = []
        api_mgr.create_records_from_objects(resources)
        resources = []

if datasets:
    api_mgr.create_records_from_objects(datasets)
if resources:
    api_mgr.create_records_from_objects(resources)
