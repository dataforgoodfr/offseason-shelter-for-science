import argparse
import csv
import pathlib
import time
from enum import Enum

import nocodb.tables
from nocodb.api import Manager as APIManager
from nocodb.models import Resource
from nocodb.project import Project
from nocodb.utils import CustomThread

URL = "https://noco.services.dataforgood.fr"

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

DEFAULT_DATA_DB_PATH = SCRIPT_DIR.parent / "data/db"
DEFAULT_PROJECT_PATH = DEFAULT_DATA_DB_PATH / "projects.json"
DEFAULT_PROJECT_NAME = "offseason_us_climate_data"

CSV_DELIMITER = ","
CSV_QUOTE_CHAR = '"'


class ProcessStatus(Enum):

    FAILED = "F"
    SUCCESS = "S"


def process_resource(raw_resource: dict) -> list:
    try:
        resource = Resource.from_nocodb_dict(raw_resource)
        head_info = resource.retrieve_head_info()
    except Exception:
        return [
            raw_resource["Id"],
            raw_resource["dg_id"],
            None,
            None,
            ProcessStatus.FAILED.value,
        ]
    return [
        resource.id,
        resource.dg_data.id,
        head_info.content_length,
        head_info.content_type,
        ProcessStatus.SUCCESS.value,
    ]


argparser = argparse.ArgumentParser()
argparser.add_argument("output_file")

argparser.add_argument(
    "--project-name", default=DEFAULT_PROJECT_NAME, help="NOCODB project name"
)
argparser.add_argument(
    "--project-path", default=DEFAULT_PROJECT_PATH, help="Path to NOCODB project file."
)

args = argparser.parse_args()


api_mgr = APIManager(URL, Project(args.project_path, args.project_name))
content = api_mgr.list_records(nocodb.tables.TABLE_DG_RESOURCES)
total_rows = content.page_info.total_rows

print(f"Prepare to handle {total_rows} resources...")
with open(args.output_file, "a") as output_file:
    csv_writer = csv.writer(
        output_file,
        delimiter=CSV_DELIMITER,
        quotechar=CSV_QUOTE_CHAR,
        quoting=csv.QUOTE_NONNUMERIC,
    )
    csv_writer.writerow(
        ["id", "dg_id", "content_length", "content_type", "process_status"]
    )
for offset in range(0, total_rows, 25):
    request_threads = []
    if offset % 1000 == 0:
        print(f"Processing {offset} -> {offset + 999}...")
    content = api_mgr.list_records(nocodb.tables.TABLE_DG_RESOURCES, offset=offset)
    for entry in content.list:
        thread = CustomThread(target=process_resource, args=(entry,))
        thread.start()
        request_threads.append(thread)

    for request_thread in request_threads:
        with open(args.output_file, "a") as output_file:
            csv_writer = csv.writer(
                output_file,
                delimiter=CSV_DELIMITER,
                quotechar=CSV_QUOTE_CHAR,
                quoting=csv.QUOTE_NONNUMERIC,
            )
            csv_writer.writerow(request_thread.join())
time.sleep(5)  # Just make sure all threads are over
