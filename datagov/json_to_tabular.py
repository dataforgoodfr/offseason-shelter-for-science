# coding: utf-8

import argparse
import datetime
import pathlib
import re

from tqdm import tqdm

from ckan.package_search import DatasetLoader

from tabular.builder import Builder

"""
Crawls through directories searching for package_search results, building tabular files.
"""

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

DEFAULT_OUTPUT_DIR = SCRIPT_DIR.parent / "data/output"

argparser = argparse.ArgumentParser()
argparser.add_argument("input", type=pathlib.Path, help="Input directory")
argparser.add_argument(
    "output", type=pathlib.Path, default=DEFAULT_OUTPUT_DIR, help="Output directory"
)
argparser.add_argument("path_regex")
argparser.add_argument(
    "--dataset-fields",
    type=list,
    default=["id", "name", "access_directdl_count", "access_total_count"],
)
argparser.add_argument(
    "--resource-fields", type=list, default=["id", "dataset_id", "url", "resource_type"]
)
argparser.add_argument("--output-prefix")
argparser.add_argument("--organization")
argparser.add_argument("--format", default="csv")

args = argparser.parse_args()

args.input = args.input.resolve(strict=True)

output_dir = args.output / (
    f"tab_data_gov_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
)

path_regex = re.compile(args.path_regex)

loader = DatasetLoader()

# First pass for progress bar total count.
total_count = len(
    [item for item in args.input.rglob("*.json") if path_regex.match(str(item))]
)

tabular_builder = Builder(
    output_format=args.format,
    dataset_fields=args.dataset_fields,
    resource_fields=args.resource_fields,
)

progress = tqdm(total=total_count)
for item in args.input.rglob("*.json"):
    match_res = path_regex.match(str(item))
    if not match_res:
        continue

    query_result = loader.load(item, resources=True)
    for dataset in query_result.datasets.values():
        tabular_builder.add_dataset(dataset)

    progress.update(1)

progress.close()

tabular_builder.write(output_dir, name="datagov", prefix=args.output_prefix)
