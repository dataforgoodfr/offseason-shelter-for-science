# coding: utf-8

import argparse
import datetime
import json
import pathlib

import pandas as pd

_SCRIPT_DIR = pathlib.Path(__file__).parent
_DATA_DIR = _SCRIPT_DIR / "data"
DEFAULT_OUTPUT_DIR = _DATA_DIR / "results"

argparser = argparse.ArgumentParser("Script to convert AI responses to human-readable results.")
argparser.add_argument("input_file", type=pathlib.Path, help="Path to the JSON file containing dataset information")
argparser.add_argument("csv_directory", type=pathlib.Path, help="Directory containing the CSV files")
argparser.add_argument("--output-directory", type=pathlib.Path, default=DEFAULT_OUTPUT_DIR, help="Directory to save the output file")

args = argparser.parse_args()

datasets = {}

dataset_info = json.load(args.input_file.open("r", encoding="utf-8"))

# Building dataset dictionnary
for organization, info in dataset_info.items():
    if "datasets" not in info:
        raise ValueError(f"No datasets found for organization {organization}")

    for ds in info["datasets"]["items"]:
        if "id" not in ds:
            raise ValueError(f"No id found for dataset {ds} in organization {organization}")
        
        if ds["id"] in datasets:
            raise ValueError(f"Duplicate dataset id {ds['id']} found in organization {organization}")
        
        ds["org"] = organization
        datasets[ds["id"]] = ds

print(json.dumps(datasets, indent=2, ensure_ascii=False))

output_df = pd.DataFrame(columns=[
    "Organization", "ID", "DG_ID", "Name", "Nature of Use", "Personas", "Title", "Notes"
])

for csv_file in args.csv_directory.rglob("*.csv"):
    print(f"Processing {csv_file}...")
    df = pd.read_csv(csv_file)
    for _, row in df.iterrows():
        ds_id = row["ID"]
        if ds_id not in datasets:
            raise ValueError(f"Dataset id {ds_id} not found in dataset information")

        ds = datasets[ds_id]
        output_df.loc[-1] = [
            ds["org"], ds_id, ds["dg_id"], ds["dg_name"], row["Nature of Use"], row["Personas"], ds["dg_title"], ds["dg_notes"].replace("\r\n", " ").replace("\n", " ")
        ]
        output_df.index += 1

file_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_df.to_csv(args.output_directory / f"dataset_summary_{file_time}.csv", index=False)
