# coding: utf-8

import argparse
import datetime
import logging
import pathlib
import re
from tqdm import tqdm

from ckan.package_search import DatasetLoader
from asset.collector.manager import Manager

"""
Crawls through directories searching for package_search results, writing asset files.
"""

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
_DATA_DIR = _SCRIPT_DIR.parent.parent / "data"
_LOG_DIR = _DATA_DIR / "log"
DEFAULT_OUTPUT_DIR = _DATA_DIR / "output"

_MAX_RETRIES = 3
_TIMEOUT = datetime.timedelta(seconds=300.0)

_file_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

argparser = argparse.ArgumentParser()
argparser.add_argument("input", type=pathlib.Path, help="Input directory")
argparser.add_argument("path_regex")
argparser.add_argument("--organization")
argparser.add_argument(
    "--scrapy-storage-dir",
    type=pathlib.Path,
    default=DEFAULT_OUTPUT_DIR / "scrapy_storage",
    help="Directory for Scrapy storage",
)
argparser.add_argument(
    "--force",
    action="store_true",
    help="Retrieve assets even if resource directory exists.",
)

args = argparser.parse_args()
print(vars(args))
args.input = args.input.resolve(strict=True)

path_regex = re.compile(args.path_regex)
print(path_regex)
loader = DatasetLoader()

# First pass for progress bar total count.
json_total_count = len(
    [item for item in args.input.rglob("*.json") if path_regex.match(str(item))]
)

manager = Manager({
        "RETRY_TIMES": _MAX_RETRIES,
        "DOWNLOAD_TIMEOUT": _TIMEOUT.total_seconds(),
        "LOG_FILE": _LOG_DIR / f"{_file_datetime}_scrapy.log",
        "LOG_FORMAT": "%(asctime)s - %(levelname)s - %(message)s",
        "LOG_LEVEL": logging.DEBUG,
        "ITEM_PIPELINES": {
            "asset.collector.pipelines.JsonWriterPipeline": 1,
        },
        "PIPELINE_JSON_OUTPUT_DIR": args.scrapy_storage_dir,
})

json_progress = tqdm(total=json_total_count, desc="Parsing JSON files")
for item in args.input.rglob("*.json"):
    match_res = path_regex.match(str(item))
    if not match_res:
        continue

    query_result = loader.load(item, resources=True)
    for dataset in query_result.datasets.values():
        for resource in dataset.resources.values():
            if (
                args.force
                or True
                # @todo Check if resource has already been collected
            ):
                manager.collect_later(
                    resource.url,
                    collection_name=resource.id,
                    collection_key="resource_id",
                )

    json_progress.update(1)

json_progress.close()

manager.collect(progress=True)
