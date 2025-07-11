# coding: utf-8

import argparse
import datetime
import json
import pathlib

from tqdm import tqdm

from sqlalchemy.orm import load_only

from rescue_api.models.asset import Asset, AssetKind
from rescue_api.models.resource import Resource
from rescue_api.database import get_db

_KILOBYTE = 1024
_MEGABYTE = _KILOBYTE * _KILOBYTE
_GIGABYTE = _KILOBYTE * _MEGABYTE
_TERABYTE = _KILOBYTE * _GIGABYTE

_SIZE_UNITS = {
    "K": _KILOBYTE,
    "M": _MEGABYTE,
    "G": _GIGABYTE,
    "T": _TERABYTE,
}

argparser = argparse.ArgumentParser()
argparser.add_argument("input", type=pathlib.Path, help="Input directory")
argparser.add_argument("--resources", nargs="*", type=str, default=[], help="List of resource ids to process")

args = argparser.parse_args()

args.input = args.input.resolve(strict=True)

if not args.input.is_dir():
    raise ValueError(f"Input path {args.input} is not a directory.")

targeted_resources = set(args.resources)

asset_kind_mapping = {}
resource_mapping = {}

db = next(get_db())

asset_index = 0

file_count = sum(1 for _ in args.input.rglob("*.json"))

for json_file in args.input.rglob("*.json"):
    json_obj = None

    # Check if the parent directory matches the resources filter
    if targeted_resources:
        if json_file.parent.name not in targeted_resources:
            continue

        dg_resource_id = json_obj["resource_id"]
        json_obj = json.load(json_file.open("r"))

        # Just in case the resource_id does not match the parent directory
        if dg_resource_id not in targeted_resources:
            continue
    else:
        json_obj = json.load(json_file.open("r"))
    
    dg_resource_id = json_obj["resource_id"]
    assets = json_obj.get("assets", [])

    for json_asset in tqdm(assets, desc=f"Processing assets in {json_file.name}", total=len(assets), unit="asset"):
        asset_index += 1

        modified = json_asset["modified"]
        url = json_asset["url"]
        size = json_asset["size"]
        
        kind_name = Resource.get_type_from_url(url)
        if kind_name in ["dir", "web"]:
            raise ValueError(f"Invalid asset kind '{kind_name}' for URL: {url}")

        if kind_name not in asset_kind_mapping:
            # Retrieve asset kind from the database or create a new one
            existing_kind = db.query(AssetKind).filter(AssetKind.name == kind_name).options(load_only(AssetKind.id)).one_or_none()
            if existing_kind:
                asset_kind_mapping[kind_name] = existing_kind.id
            else:
                asset_kind = AssetKind(name=kind_name)
                db.add(asset_kind)
                db.commit()
                
                asset_kind_mapping[kind_name] = asset_kind.id
        if dg_resource_id not in targeted_resources:
            existing_resource = db.query(Resource).filter(Resource.dg_id == dg_resource_id).options(load_only(Resource.id)).one_or_none()
            if existing_resource:
                resource_mapping[dg_resource_id] = existing_resource
            else:
                raise ValueError(f"Resource with ID {dg_resource_id} not found in the database.")
        
        asset = Asset()
        asset.kind_id = asset_kind_mapping[kind_name]
        asset.resource = resource_mapping[dg_resource_id]
        asset.url = url
        
        if size[-1].upper() == "B":
            size = size[:-1].strip()
        size_unit = size[-1].upper()
        if size_unit in _SIZE_UNITS:
            size = float(size[:-1].strip()) * _SIZE_UNITS[size_unit]
        size = int(size)  # Ensure size is an integer
        
        asset.size = size
        asset.mtime = datetime.datetime.strptime(modified, "%Y-%m-%d %H:%M")

        db.add(asset)
        if asset_index % 5000 == 0:
            db.commit()

db.commit()

print(f"Total assets processed: {asset_index}")