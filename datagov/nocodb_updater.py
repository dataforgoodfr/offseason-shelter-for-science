# coding: utf-8

import argparse
import pathlib
import sys

from nocodb.api import Manager as APIManager
from nocodb.project import Project
from nocodb.updaters import *

"""
Updates a whole NOCODB table.
"""

URL = "https://noco.services.dataforgood.fr"

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

DEFAULT_DATA_DB_PATH = SCRIPT_DIR.parent / "data/db"
DEFAULT_PROJECT_PATH = DEFAULT_DATA_DB_PATH / "projects.json"
DEFAULT_PROJECT_NAME = "offseason_us_climate_data_preprod"

argparser = argparse.ArgumentParser()

argparser.add_argument("updater", help="Updater class name.")
argparser.add_argument(
    "--where",
    type=str,
    help='NOCODB where expression. See "List Table Records" API method documentation.',
)
argparser.add_argument(
    "--project-name", default=DEFAULT_PROJECT_NAME, help="NOCODB project name"
)
argparser.add_argument(
    "--project-path", default=DEFAULT_PROJECT_PATH, help="Path to NOCODB project file."
)

args = argparser.parse_args()

api_mgr = APIManager(URL, Project(args.project_path, args.project_name))

# Creating updater object
updater = getattr(sys.modules[__name__], args.updater)(api_mgr)
updater.update(where=args.where)
