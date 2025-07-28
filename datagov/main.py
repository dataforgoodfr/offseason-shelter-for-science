# coding: utf-8

from scrapy.settings import Settings
from asset.collector.manager import Manager


def main():
    settings = Settings()
    settings.setmodule('scrapy.settings.default_settings', priority='default')
    
    settings.set('ITEM_PIPELINES', {
        'pipelines.JsonWriterPipeline': 300,
    })
    settings.set('PIPELINE_JSON_OUTPUT_DIR', './output')
    settings.set('LOG_LEVEL', 'INFO')
    
    manager = Manager(settings)
    
    print("Planification des collectes...")
    
    success = manager.collect_later(
        "https://www.ncei.noaa.gov/pub/data/hourly_precip-3240/",
        collection_name="Climate_Data",
        collection_key="dataset"
    )
    

    
    print(f"Collectes planifiées: {manager.collect_count}")
    print(f"Résultats: {success=}")
    
    manager.collect(progress=True)
    

if __name__ == "__main__":
    main()
