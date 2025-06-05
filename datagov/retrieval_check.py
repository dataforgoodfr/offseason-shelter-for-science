# coding: utf-8

import argparse
import pathlib
import re

from ckan.package_search import DatasetLoader

"""
Crawls through directories searching for package_search results, verifying result count and uniqueness.
"""

argparser = argparse.ArgumentParser()
argparser.add_argument("directory", type=pathlib.Path)
argparser.add_argument("path_regex")

args = argparser.parse_args()

args.directory = args.directory.resolve(strict=True)

path_regex = re.compile(args.path_regex)

loader = DatasetLoader()

total_count = 0

for item in args.directory.rglob("*.json"):
    match_res = path_regex.match(str(item))
    if not match_res:
        continue

    loader.load(item)

    if total_count < loader.expected_count():
        total_count = loader.expected_count()
        print("New count:", total_count)

print(loader.parsed_count(), "/", loader.expected_count())
print("Duplicates:", loader.duplicate_count())
