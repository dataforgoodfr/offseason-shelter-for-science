# coding: utf-8

import pandas as pd

_ENGINE_MAPPING = {"xlsx": "xlswriter"}

from ckan.dataset import Dataset


class UnknownFormatError(Exception):
    pass


class Builder:
    def __init__(self, output_format="csv", dataset_fields=None, resource_fields=None):
        self.format = self.ext = output_format.lower()
        self.dataset_fields = dataset_fields
        self.resource_fields = resource_fields

        if output_format != "csv":
            self.engine = self.get_engine()

        self.organizations = {}
        self.datasets = {}
        self.resources = {}
        self.assets = {}

    def get_engine(self) -> str:
        if self.format not in _ENGINE_MAPPING:
            raise UnknownFormatError(self.format)

    def add_dataset(self, dataset: Dataset):
        organization_id = dataset.organization.id
        if not organization_id in self.organizations:
            self.organizations[organization_id] = dataset.organization
            self.datasets[organization_id] = {}
            self.resources[organization_id] = {}
            self.assets[organization_id] = {}

        self.datasets[organization_id][dataset.id] = dataset

        for resource in dataset.resources.values():
            self.resources[organization_id][resource.id] = resource

    def write(self, output_dir, name="datagov", prefix=None):
        for organization_id, organization in self.organizations.items():
            filename = f"{name}_{organization.name}"

            if prefix:
                filename = prefix + "_" + filename

            organization_df = self.create_data_frame(
                organization_id, self.organizations
            )
            dataset_df = self.create_data_frame(
                organization_id, self.datasets, fields=self.dataset_fields
            )
            resource_df = self.create_data_frame(
                organization_id, self.resources, fields=self.resource_fields
            )
            assets_df = self.create_data_frame(
                organization_id, self.assets, fields=["id", "name", "url"]
            )

            if self.datasets[organization_id]:
                output_dir.mkdir(exist_ok=True)

                if self.format == "csv":
                    organization_df.to_csv(
                        output_dir / f"{filename}_organization.{self.ext}",
                        encoding="utf-8",
                        index=False,
                    )
                    dataset_df.to_csv(
                        output_dir / f"{filename}_dataset.{self.ext}",
                        encoding="utf-8",
                        index=False,
                    )
                    resource_df.to_csv(
                        output_dir / f"{filename}_resource.{self.ext}",
                        encoding="utf-8",
                        index=False,
                    )
                    assets_df.to_csv(
                        output_dir / f"{filename}_asset.{self.ext}",
                        encoding="utf-8",
                        index=False,
                    )
                else:
                    with pd.ExcelWriter(
                        output_dir / f"{filename}.{self.ext}", engine=self.engine
                    ) as writer:
                        organization_df.to_excel(
                            writer, sheet_name="Organizations", index=False
                        )
                        dataset_df.to_excel(writer, sheet_name="Datasets", index=False)
                        resource_df.to_excel(
                            writer, sheet_name="Resources", index=False
                        )

    def create_data_frame(self, organization_id, objects, fields=None):
        result = None

        if fields:
            result = pd.DataFrame(
                [
                    {field: item.__dict__[field] for field in fields}
                    for item in objects[organization_id].values()
                ]
            )
        else:
            o = vars(objects[organization_id])
            del o["obj"]  # Removing "obj" property
            result = pd.DataFrame([o])

        return result
