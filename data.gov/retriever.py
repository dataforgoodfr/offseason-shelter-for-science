# coding: utf-8

import argparse
import datetime
import json
import os
import pathlib

from ckan.package_search import Searcher

# -----

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

DEFAULT_OUTPUT_DIR = SCRIPT_DIR.parent / 'data/output'

DEFAULT_URL = 'https://catalog.data.gov'

argparser = argparse.ArgumentParser(description="Fetch data.gov metadata.")
argparser.add_argument("organization", help="data.gov organization.")
argparser.add_argument("--url", type=str, default=DEFAULT_URL, help="URL to fetch data from")
argparser.add_argument("--start", type=int, default=0, help="CKAN 'start' parameter.")
argparser.add_argument("--rows", type=int, default=None, help="CKAN 'rows' parameter.")
argparser.add_argument("--output-dir", type=pathlib.Path, default=DEFAULT_OUTPUT_DIR)
argparser.add_argument("--limit", type=int)
argparser.add_argument("--full", action='store_true', help="Download all datasets starting from 'start' parameter.")

args = argparser.parse_args()

# Checking output dir exists
args.output_dir.resolve(strict=True).is_dir()

output_dir = args.output_dir / (f'data_gov_{args.organization}_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
output_prefix='package_search'

# Init
searcher = Searcher(args.url, output_dir=output_dir, output_prefix=output_prefix)
searcher.set_organization(args.organization)
searcher.build_query_params()

if args.full or args.limit:
    searcher.search(start=args.start, rows=args.rows, limit=args.limit, sleep=15, retries=3)
else:
    package_search_res = searcher.request(start=args.start, rows=args.rows)
    searcher.write_last_result(output_dir, prefix=output_prefix)
