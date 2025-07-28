# coding: utf-8

import datetime
import json
import pathlib

from itemadapter import ItemAdapter


class JsonWriterPipeline:
    def __init__(self, output_dir):
        self.output_dir = pathlib.Path(output_dir)
        self.item_index = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            output_dir=crawler.settings.get("PIPELINE_JSON_OUTPUT_DIR"),
        )

    def process_item(self, item, spider):
        output_dir = self.output_dir / f"{spider.collection_name}"
        output_path = (output_dir / f"{self.item_index:04d}").with_suffix(".json")

        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)

        with output_path.open("w") as output_file:
            output_file.write(json.dumps(ItemAdapter(item).asdict(), indent=4) + "\n")
        self.item_index += 1
        return item
