# coding: utf-8

import json
import pathlib
import time
from tqdm import tqdm

from ckanapi import RemoteCKAN

from .model_manager import ModelManager

from rescue_db.rescue_api.models.organization import Organization

class QueryResult:
    def __init__(self, packages, model_manager: ModelManager = None):
        self.packages = packages
        self.model_manager = model_manager if model_manager else ModelManager()

        self.total_count = packages["count"] if "count" in packages else None

        self.count = 0
        if "results" in packages:
            self.count = len(packages["results"])

        if self.total_count:
            self.total_count_digits = len(str(self.total_count))

    def parse_results(self, resources=False):
        for dataset_obj in self.packages["results"]:
            self.model_manager.create_dataset(dataset_obj, resources=resources)

    def is_empty(self) -> bool:
        return not self.count

    def write(self, output_path):
        # Writes the output
        with output_path.open("w") as output_file:
            json.dump(self.packages, output_file, indent=4)


# -----


class Searcher:
    def __init__(self, url, output_dir: pathlib.Path = None, output_prefix: str = None):
        self.url = url
        self.output_dir = output_dir
        self.output_prefix = output_prefix

        self.reset()

    def reset(self):
        self.remote_ckan = RemoteCKAN(self.url)

        self.last_result = None
        self.last_query = None

        self.query = None
        self.filter_query = None

        self.organization = None

    def set_organization(self, organization):
        self.organization = organization

    def build_query_params(self):
        if self.organization:
            self.filter_query = f"+organization:{self.organization}"

    # action.package_search request.
    def request(self, start=None, rows=None) -> QueryResult:
        self.last_query = {}
        if self.query:
            self.last_query["q"] = self.query

        if self.filter_query:
            self.last_query["fq"] = self.filter_query

        if start is not None:
            self.last_query["start"] = start
        if rows is not None:
            self.last_query["rows"] = rows

        self.last_result = QueryResult(
            self.remote_ckan.action.package_search(**self.last_query)
        )

        return self.last_result

    def search(self, start=None, rows=None, limit=None, sleep=None, retries=None):
        total_expected = 0
        total_retrieved = 0

        if start is None:
            start = 0

        progress = None

        while not self.last_result or not self.last_result.is_empty():
            try:
                self.request(start=start, rows=rows)
            except ckanapi.errors.CKANAPIError as api_error:
                if not retries:
                    raise api_error

                if api_error.status == 502:
                    retries -= 1
                    if sleep:
                        time.sleep(sleep)

                    continue

            if not total_expected:
                total_expected = self.last_result.total_count
                progress = tqdm(total=total_expected)

            progress.update(self.last_result.count)
            total_retrieved += self.last_result.count

            if limit:
                limit -= self.last_result.count

                if limit <= 0:
                    break

            # Updating start for next request.
            start += self.last_result.count

            if self.output_dir and self.output_prefix:
                self.write_last_result(self.output_dir, self.output_prefix)

        progress.close()
        print(f"Expected: {total_expected}, Retrieved: {total_retrieved}")

    # Writes last request result to a file.
    def write_last_result(self, output_dir: pathlib.Path, prefix: str = None):
        if not prefix:
            prefix = "searcher"

        # Building file path
        name = prefix

        if "start" in self.last_query and self.last_result.total_count:
            # Zero padding "start" according to total count digits.
            name += (
                "_S{start:0" + str(self.last_result.total_count_digits) + "}"
            ).format(start=self.last_query["start"])

        if "rows" in self.last_query:
            name += "_R{0}".format(self.last_query["rows"])

        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / (name + ".json")
        self.last_result.write(output_path)


# -----


class DatasetLoader:
    def __init__(self, exists_ok=False):
        self.path = None
        self.query_result = None
        self.exists_ok = exists_ok
        self.model_manager = ModelManager(exists_ok=exists_ok)

        self.datasets = {}
        self.duplicates = []

        self.total_count = 0

    def load(self, path: pathlib.Path, resources=False) -> QueryResult:
        self.path = path

        self.query_result = QueryResult(
            json.load(path.open("r")),
            model_manager=self.model_manager,
        )
        self.query_result.parse_results(resources=resources)

        # Adding datasets one by one to filter duplicates.
        # for dataset_id, dataset in self.query_result.datasets.items():
        #    if dataset_id in self.datasets:
        #        print("id already exists", dataset_id)
        #        self.duplicates.append(dataset)
        #        continue

        #    self.datasets[dataset_id] = dataset

        if self.query_result.total_count > self.total_count:
            self.total_count = self.query_result.total_count

        return self.query_result

    def expected_count(self) -> int:
        return self.total_count

    def parsed_count(self) -> int:
        return len(self.datasets.keys())

    def duplicate_count(self) -> int:
        return len(self.duplicates)
