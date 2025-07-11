# coding: utf-8

import json
import logging

from rescue_db.rescue_api.models.organization import Organization
from rescue_db.rescue_api.models.dataset import Dataset
from rescue_db.rescue_api.models.resource import Resource
from rescue_db.rescue_api.models.dataset_json import DatasetJson


class ModelManager:
    # @todo : cache optimization. Only keep id and modification date.
    def __init__(self, exists_ok=False):
        self.organizations = {}
        self.datasets = {}
        self.dataset_jsons = {}
        self.resources = {}
        self.exists_ok = exists_ok

    def get_organizations(self) -> list[Organization]:
        """
        Returns a list of organizations.
        """
        return list(self.organizations.values())

    def get_datasets(self) -> list[Dataset]:
        """
        Returns a list of datasets.
        """
        return list(self.datasets.values())

    def create_organization(self, obj) -> Organization:
        organization = None
        dg_id = obj["id"]
        if dg_id in self.organizations:
            organization = self.organizations[dg_id]
            # No update needed, as we assume the organization object is immutable.
        else:
            organization = Organization()

            organization.dg_id = dg_id
            organization.dg_name = obj["name"]
            organization.dg_title = obj["title"]
            organization.dg_created = obj["created"]

            self.organizations[dg_id] = organization

        return organization

    def create_dataset(self, obj, resources=False) -> Dataset:
        dataset = None
        dg_id = obj["id"]
        dg_metadata_modified = obj["metadata_modified"]

        if dg_id in self.datasets:
            if not self.exists_ok:
                raise Exception(f"Dataset {dg_id} already exists.")

            if dg_metadata_modified > self.datasets[dg_id].dg_metadata_modified:
                logging.warning(
                    f"Dataset {dg_id} encountered with a newer metadata_modified, updating."
                )
                dataset = self.datasets[dg_id]
                dataset.dg_metadata_modified = dg_metadata_modified
                dataset.json_data.content = json.dumps(
                    obj, ensure_ascii=False, indent=2
                )

            else:
                logging.warning(
                    f"Dataset {dg_id} already exists with a newer metadata_modified, skipping."
                )
                return self.datasets[dg_id]

        if not dataset:
            dataset = Dataset()
            dataset.dg_id = obj["id"]
            dataset.dg_metadata_modified = dg_metadata_modified

            organization = self.create_organization(obj["organization"])
            organization.datasets.append(dataset)

            dataset.organization = organization
            dataset_json = DatasetJson()
            dataset_json.dataset = dataset
            dataset_json.content = json.dumps(obj, ensure_ascii=False, indent=2)

            dataset.json_data = dataset_json

            self.datasets[dataset.dg_id] = dataset

        dataset.dg_name = obj["name"]
        dataset.dg_title = obj["title"]
        dataset.dg_notes = obj["notes"]
        dataset.dg_metadata_created = obj["metadata_created"]

        # dataset_model.state = dataset_obj["state"]

        dataset.access_direct_dl_count = 0
        dataset.access_total_count = 0

        if resources and "resources" in obj:
            for resource_obj in obj["resources"]:
                resource = self.create_resource(resource_obj)

                if resource.resource_type:
                    dataset.access_total_count += 1

                    if resource.resource_type not in ["web", "dir"]:
                        dataset.access_direct_dl_count += 1

                resource.dataset = dataset
                dataset.resources.append(resource)

        return dataset

    def create_resource(self, obj) -> Resource:
        resource = None
        dg_id = obj["id"]
        dg_metadata_modified = obj["metadata_modified"]

        if dg_id in self.resources:
            if not self.exists_ok:
                raise Exception(f"Resource {dg_id} already exists.")

            if dg_metadata_modified > self.resources[dg_id].dg_metadata_modified:
                logging.warning(f"Resource {dg_id} already exists, updating.")
                resource = self.resources[dg_id]
                resource.dg_metadata_modified = dg_metadata_modified
            else:
                logging.warning(
                    f"Resource {dg_id} already exists with a newer metadata_modified, skipping."
                )
                return self.resources[dg_id]

        if not resource:
            resource = Resource()
            resource.dg_id = dg_id
            resource.dg_metadata_modified = dg_metadata_modified

            self.resources[resource.dg_id] = resource

        resource.dg_name = obj["name"]
        resource.dg_description = obj["description"]

        resource.dg_resource_locator_function = (
            obj["resource_locator_function"]
            if "resource_locator_function" in obj
            else None
        )
        resource.dg_resource_locator_protocol = (
            obj["resource_locator_protocol"]
            if "resource_locator_protocol" in obj
            else None
        )
        resource.dg_mimmetype = obj["mimetype"] if "mimetype" in obj else None

        resource.dg_state = obj["state"]
        resource.set_url(obj["url"])

        resource.dg_created = obj["created"]

        return resource
