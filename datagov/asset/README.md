# Web Scraper Docker - Guide d'installation et d'utilisation

## Structure des répertoires


```
datago/asset/                    # Répertoire racine pour le scraping
├── manager.py                  
├── collector.py
├── link_scraper.py
├── spiders/
│   └── link_spider.py
├── pipelines/
│   └── file_info_pipeline.py
├── docker-compose.yml          
├── Dockerfile                  
├── requirements.txt            
├── main.py             
├── deploy.sh                  
├── output/                    
├── logs/                      
└── README.md                  
```

## Installation rapide

### 0. Prérequis

Assurez-vous d'avoir installé :
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Vérifiez l'installation :
```bash
docker --version
docker compose version
```

Ces differentes commandes doivent se faire dans le repertoire racine du projet ou se trouve le docker compose

### 2. Construction de l'image Docker
```bash
docker compose build 
```

### 3. Démarrer le service de scrapping
```bash
docker compose up
```


### 4. Arrêt ou interruption du scraping
```bash
docker stop web-scraper-app
```


### 5. Logs de l'application
```bash
docker compose logs web-scraper 
```
ou
```bash
docker compose logs -f web-scraper  # En temps réel
```


