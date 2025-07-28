# coding: utf-8
# main_docker.py - Version adaptée pour Docker
import os
import sys
import logging
from manager import Manager
from pipelines.file_info_pipeline import FileInfoPipeline

def setup_logging():
    """Configure le logging pour Docker"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/app/logs/scraper.log')
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Récupérer les variables d'environnement
    base_url = os.getenv('SCRAPER_URL', 'https://example.com')
    collection_name = os.getenv('COLLECTION_NAME', 'default_scraping')
    output_format = os.getenv('OUTPUT_FORMAT', 'json')
    concurrent_requests = int(os.getenv('CONCURRENT_REQUESTS', '16'))
    download_delay = float(os.getenv('DOWNLOAD_DELAY', '1'))
    
    logger.info(f"Démarrage du scraping pour: {base_url}")
    logger.info(f"Collection: {collection_name}")
    logger.info(f"Format de sortie: {output_format}")
    
    # Configuration Scrapy
    settings = {
        'USER_AGENT': 'LinkScraper Docker (+http://www.yourdomain.com)',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': concurrent_requests,
        'DOWNLOAD_DELAY': download_delay,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'ITEM_PIPELINES': {
            'pipelines.file_info_pipeline.FileInfoPipeline': 300,
        },
        'PIPELINE_OUTPUT_DIR': '/app/output',
        'OUTPUT_FORMAT': output_format,
        'LOG_LEVEL': 'INFO',
        'FEEDS': {
            f'/app/output/{collection_name}/results.json': {
                'format': 'json',
                'overwrite': True,
            }
        }
    }
    
    # Configuration Redis
    redis_config = {
        'host': 'redis',        # Adresse Redis
        'port': 6379,              # Port Redis
        'db': 0,                   
        'password': None,          
        'expiry_hours': 24         
    }
    
    try:
        manager = Manager(settings, redis_config)
        
        if manager.collect_later(base_url, collection_name=collection_name):
            logger.info(f"Scraping programmé pour: {base_url}")
            
            # Lancer la collecte avec barre de progression
            manager.collect(progress=True)
            logger.info("Scraping terminé avec succès")
        else:
            logger.error("Aucun collecteur trouvé pour cette URL")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Erreur lors du scraping: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()