# coding: utf-8

import argparse
import pathlib
import re
from tqdm import tqdm

from ckan.package_search import DatasetLoader

from rescue_db.rescue_api import database

"""
Crawls through directories searching for package_search results filling the database.
"""

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

argparser = argparse.ArgumentParser()
argparser.add_argument("input", type=pathlib.Path, help="Input directory to crawl in.")
argparser.add_argument(
    "path_regex", help="File path regular expression to filter input files."
)

argparser.add_argument(
    "--dataset-batch-size",
    default=500,
    help="Number of datasets to insert in a single transaction for big organizations.",
)

args = argparser.parse_args()

args.input = args.input.resolve(strict=True)

# Checking existing organizations in DB.
# @todo : Several scripts running concurrently could lead to organization duplicates
existing_organizations = {}

path_regex = re.compile(args.path_regex)

loader = DatasetLoader(exists_ok=True)

file_index = 0

# First pass to count items.
file_count = len([item for item in args.input.rglob("*.json") if path_regex.match(str(item))])

db = next(database.get_db())
progress = tqdm(total=file_count, desc="Processing files", unit="file")

for item in args.input.rglob("*.json"):
    match_res = path_regex.match(str(item))
    if not match_res:
        continue

    query_result = loader.load(item, resources=True)

    # file_index += 1

    # if not query_result.is_empty():
    #     organizations = query_result.model_manager.get_organizations()
    #     for organization in organizations:
    #         db.merge(organization)
    #         db.commit()
    
    progress.update(1)

progress.close()

# Second pass to insert organizations.

# Counting
organization_count = len(loader.model_manager.organizations)
print(f"Found {organization_count} organizations.")

dataset_count = len(loader.model_manager.datasets)
print(f"Found {dataset_count} datasets.")

resource_count = len(loader.model_manager.resources)
print(f"Found {resource_count} resources.")

progress = tqdm(total=dataset_count, desc="Inserting datasets", unit="dataset")

organizations = loader.model_manager.get_organizations()
for organization in organizations:
    org_dataset_count = len(organization.datasets)
    if org_dataset_count <= 30000:
        progress.set_description(f"Inserting {organization.dg_name} datasets")
        db.merge(organization)
        db.commit()

        progress.update(org_dataset_count)
    else:
        # Organization has too many datasets, handling separately
        # progress.set_description(f"Organization {organization.dg_name} has too many datasets ({org_dataset_count}). Handling separately.")

        # Detaching datasets from organization to insert them in batches
        org_datasets = list(organization.datasets)  # Save the list
        organization.datasets = []
        
        db.add(organization)
        db.commit()

        i = 0
        pending_commit_datasets = []

        for dataset in org_datasets:
            i += 1
            
            dataset.organization = organization
            db.add(dataset)
            progress.update(1)

            if i % args.dataset_batch_size == 0:
                db.commit()

                for pending_dataset in pending_commit_datasets:
                    # Freeing memory
                    del pending_dataset
        
        db.commit()
    
    # Freeing memory
    del organization

progress.close()

    # Inserting every "batch size" file parsed
#    if (file_index % args.batch_size) == 0:
#        print(file_index, "/", file_count)

