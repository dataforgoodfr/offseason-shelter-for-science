# coding: utf-8

import argparse
import datetime
import pathlib
import json

from ckan.package_search import DatasetLoader

argparser = argparse.ArgumentParser()
argparser.add_argument(
    "input",
    type=pathlib.Path,
)
argparser.add_argument(
    "output",
    type=pathlib.Path,
)
args = argparser.parse_args()

resource_url_mapping = {}

args.input = args.input.resolve()

for item in args.input.rglob("*/package_search*.json"):
    ds_loader = DatasetLoader()
    ds_loader.load(item, resources=True)
    relative_path = str(item.resolve().relative_to(args.input))
    print(relative_path)
    for dataset in ds_loader.datasets.values():
        for resource in dataset.resources.values():
            url = resource.url.lower()
            if not url in resource_url_mapping:
                resource_url_mapping[url] = []
            resource_url_mapping[url].append(
                {
                    "path": relative_path,
                    "ds_id": dataset.id,
                    "res_id": resource.id,
                }
            )
file_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = args.output / f"resource_url_mapping_{file_datetime}.json"

with output_path.open("w") as output_file:
    json.dump(
        {"root": str(args.input), "mapping": resource_url_mapping},
        output_file,
        indent=4,
    )
