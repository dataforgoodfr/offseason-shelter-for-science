# coding: utf-8
import json
import pathlib
import csv
from itemadapter import ItemAdapter
from datetime import datetime

class FileInfoPipeline:
    def __init__(self, output_dir, output_format='json'):
        self.output_dir = pathlib.Path(output_dir)
        self.output_format = output_format
        self.items = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            output_dir=crawler.settings.get("PIPELINE_OUTPUT_DIR", "output"),
            output_format=crawler.settings.get("OUTPUT_FORMAT", "json")
        )

    def open_spider(self, spider):
        self.items = []

    def process_item(self, item, spider):
        self.items.append(ItemAdapter(item).asdict())
        return item

    def close_spider(self, spider):
        if not self.items:
            return

        collection_name = getattr(spider, 'collection_name', 'default')
        output_dir = self.output_dir / collection_name
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.output_format == 'json':
            output_file = output_dir / f"downloadable_files_{timestamp}.json"
            with output_file.open('w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': timestamp,
                    'base_url': spider.start_url,
                    'total_files': len(self.items),
                    'files': self.items
                }, f, indent=2, ensure_ascii=False)
                
        elif self.output_format == 'csv':
            if self.items:
                output_file = output_dir / f"downloadable_files_{timestamp}.csv"
                with output_file.open('w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.items[0].keys())
                    writer.writeheader()
                    writer.writerows(self.items)

        print(f"Saved {len(self.items)} downloadable files to {output_file}")

