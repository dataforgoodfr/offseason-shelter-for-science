# coding: utf-8
# From ./datagov/dataset_ranking_to_db.py

#import argparse
#import datetime
#import json
#import pandas as pd
#import pathlib
#import re
#from tqdm import tqdm
#
##from ckan.package_search import DatasetLoader
#
#from sqlalchemy.orm import load_only
#
##from rescue_db.rescue_api.models.dataset import Dataset
##from rescue_db.rescue_api.models.dataset_ranking import DatasetRanking
##from rescue_db.rescue_api.models.dataset_rank import DatasetRank
##
##from rescue_db.rescue_api import database
#
#_input_regex = re.compile(r"^global__(download|link)_requests.+csv$")
#
#argparser = argparse.ArgumentParser()
#argparser.add_argument(
#    "url_mapping",
#    type=pathlib.Path,
#    help="Path to the input file containing URL mappings.",
#)
#argparser.add_argument(
#    "inputs",
#    metavar="input_rankings",
#    type=pathlib.Path,
#    nargs="+",
#    help="Path to the input files containing ranking information.",
#)
#
#args = argparser.parse_args()
#
#for input_file in args.inputs:
#    input_match_res = _input_regex.match(input_file.name)
#    if not input_match_res:
#        raise ValueError(
#            f"Input file {input_file.name} does not match expected pattern."
#        )
#
#url_mapping = None
#with args.url_mapping.open("r") as url_mapping_file:
#    url_mapping = json.load(url_mapping_file)
#
#if not url_mapping or "mapping" not in url_mapping:
#    raise ValueError("Invalid URL mapping file format. 'mapping' key not found.")
#
#
#class RankedRequestManager:
#    def __init__(self, inputs: list[pathlib.Path], mapping: object):
#        self.inputs = inputs
#        self.root_path = mapping["root"]
#        self.mapping = {key.lower(): value for key, value in mapping["mapping"].items()}
#        self.rankings = {"mapping_root_path": self.root_path}
#        self.dataset_rankings = {"mapping_root_path": self.root_path}
#        self.sorted_dataset_rankings = {"mapping_root_path": self.root_path}
#        self.dataset_cache = {}
#
#        self.dataset_loader = None
#        #self.dataset_loader = DatasetLoader(exists_ok=True)
#
#    def get_dataset_info(self, ds_id: str, relative_path: str):
#        if ds_id in self.dataset_cache:
#            return self.dataset_cache[ds_id]
#
#        absolute_path = pathlib.Path(self.root_path) / relative_path
#
#        if ds_id not in self.dataset_loader.model_manager.datasets:
#            self.dataset_loader.load(absolute_path, resources=False)
#
#            if ds_id not in self.dataset_loader.model_manager.datasets:
#                raise ValueError(
#                    f"Dataset ID {ds_id} not found in the dataset loader {absolute_path}."
#                )
#
#        result = {
#            "org": self.dataset_loader.model_manager.datasets[
#                ds_id
#            ].organization.dg_name,
#            "id": ds_id,
#            "name": self.dataset_loader.model_manager.datasets[ds_id].dg_name,
#            "title": self.dataset_loader.model_manager.datasets[ds_id].dg_title,
#            "path": relative_path,
#        }
#        self.dataset_cache[ds_id] = result
#
#        return result
#
#    def rank(self):
#        rankings = {}
#
#        for input_file in self.inputs:
#            dataset_ranking = None
#            #dataset_ranking = DatasetRanking()
#            rankings[input_file.name] = dataset_ranking
#
#            dataset_ranking.name = input_file.name
#            dataset_ranking.ranking_date = datetime.datetime.fromtimestamp(
#                input_file.stat().st_ctime
#            )
#
#            input_file_name = input_file.name
#            self.rankings[input_file_name] = {}
#            self.dataset_rankings[input_file_name] = {}
#            ranking = {}
#
#            df = pd.read_csv(input_file)
#
#            if df.empty:
#                ranking = {"error": "Empty file"}
#            else:
#                link_file_type = None
#
#                # Checking file type
#                if "customEvent:DATAGOV_dataset_publisher" in df.columns:
#                    # This is a link request file
#                    print(f"Processing link requests from {input_file_name}")
#                    link_file_type = True
#
#                    dataset_ranking.type = "link"
#                    dataset_ranking.comment = "Link requests ranking"
#                elif "fileName" in df.columns:
#                    # This is a download request file
#                    print(f"Processing download requests from {input_file_name}")
#                    link_file_type = False
#
#                    dataset_ranking.type = "download"
#                    dataset_ranking.comment = "Download requests ranking"
#                else:
#                    raise ValueError(f"Unknown file format in {input_file_name}")
#
#                for index, row in tqdm(
#                    df.iterrows(),
#                    total=df.shape[0],
#                    desc=f"Processing {input_file_name}",
#                ):
#                    url = row.get("linkUrl")
#                    if url and isinstance(url, str):
#                        url = url.strip()
#
#                        publisher = None
#                        if link_file_type:
#                            publisher = row.get(
#                                "customEvent:DATAGOV_dataset_publisher", None
#                            )
#                            if publisher == "NO PUB":
#                                publisher = "Unknown"
#                        else:
#                            filename = row.get("fileName", "")
#                            if not filename:
#                                raise ValueError(
#                                    f"File name not found for download request in {input_file_name}"
#                                )
#
#                            # URL reconstruction for download requests
#                            url = url[: url.rfind("/")] + "/" + filename
#                            # print("Reconstructed URL for download request:", url)
#
#                        url_lower = url.lower()
#                        associated_resources = self.mapping.get(url_lower, [])
#                        if associated_resources:
#                            event_count = int(row.get("eventCount", 0))
#                            url_info = {
#                                "count": event_count,
#                                "page_location": row.get("pageLocation", ""),
#                                "page_title": row.get("pageTitle", ""),
#                                "index": index,
#                            }
#                            if publisher:
#                                url_info["publisher"] = publisher
#
#                            datasets = {}
#                            datasets_encountered = set()
#                            for resource in associated_resources:
#                                ds_id = resource.get("ds_id")
#                                if ds_id:
#                                    if ds_id not in datasets:
#                                        datasets[ds_id] = {
#                                            "id": ds_id,
#                                            "path": resource.get("path", ""),
#                                            "resources": {},
#                                        }
#                                    if ds_id not in datasets_encountered:
#                                        datasets_encountered.add(ds_id)
#                                        if (
#                                            ds_id
#                                            not in self.dataset_rankings[
#                                                input_file_name
#                                            ]
#                                        ):
#                                            self.dataset_rankings[input_file_name][
#                                                ds_id
#                                            ] = self.get_dataset_info(
#                                                ds_id, datasets[ds_id]["path"]
#                                            )
#                                            self.dataset_rankings[input_file_name][
#                                                ds_id
#                                            ]["count"] = event_count
#                                        else:
#                                            self.dataset_rankings[input_file_name][
#                                                ds_id
#                                            ]["count"] += event_count
#
#                                datasets[ds_id]["resources"][resource.get("res_id")] = 1
#
#                            if url_lower in ranking:
#                                ranking[url_lower]["total_count"] += url_info["count"]
#                                for ds_id, ds_info in datasets.items():
#                                    if ds_id not in ranking[url_lower]["datasets"]:
#                                        ranking[url_lower]["datasets"][ds_id] = ds_info
#                                    else:
#                                        for res_id, count in ds_info[
#                                            "resources"
#                                        ].items():
#                                            if (
#                                                res_id
#                                                in ranking[url_lower]["datasets"][
#                                                    ds_id
#                                                ]["resources"]
#                                            ):
#                                                ranking[url_lower]["datasets"][ds_id][
#                                                    "resources"
#                                                ][res_id] += 1
#                                            else:
#                                                ranking[url_lower]["datasets"][ds_id][
#                                                    "resources"
#                                                ][res_id] = count
#                                ranking[url_lower]["info"].append(url_info)
#
#                            else:
#                                ranking[url_lower] = {
#                                    "total_count": url_info["count"],
#                                    "datasets": datasets,
#                                    "info": [url_info],
#                                }
#
#            self.rankings[input_file_name] = ranking
#
#            # Sorting dataset rankings by count
#            self.dataset_rankings[input_file_name] = list(
#                self.dataset_rankings[input_file_name].values()
#            )
#            # self.sorted_dataset_rankings[input_file_name].sort(key=lambda obj: int(obj["count"]), reverse=True)
#
#        db = next(database.get_db())
#
#        dataset_db_mapping = {}
#
#        for input_file_name, ranking_datasets in self.dataset_rankings.items():
#            if input_file_name == "mapping_root_path":
#                continue  # Ignore metadata
#
#            if not ranking_datasets:
#                continue
#
#            progress = tqdm(
#                total=len(ranking_datasets),
#                desc=f"Building ranks for {input_file_name}...",
#            )
#
#            ranking = rankings[input_file_name]
#
#            rank = 0
#            sorted_datasets = sorted(
#                ranking_datasets, key=lambda x: int(x["count"]), reverse=True
#            )
#            for sorted_dataset in sorted_datasets:
#                rank += 1
#                progress.update(1)
#
#                ds_id = sorted_dataset["id"]
#                if not ds_id in dataset_db_mapping:
#                    dataset = (
#                        db.query(Dataset)
#                        .filter(Dataset.dg_id == ds_id)
#                        .options(load_only(Dataset.id))
#                        .one()
#                    )
#                    if not dataset:
#                        print("Dataset not found in DB:", ds_id, "skipping")
#                        continue
#                    dataset_db_mapping[ds_id] = dataset.id
#
#                #ranks = DatasetRank()
#                ranks = None
#                ranks.ranking = ranking
#                ranks.rank = rank
#
#                ranks.dataset_id = dataset_db_mapping[ds_id]
#                ranks.event_count = sorted_dataset["count"]
#
#            db.merge(ranking)
#            db.commit()
#            progress.close()
#
#
#ranking_manager = RankedRequestManager(args.inputs, url_mapping)
#ranking_manager.rank()
pass