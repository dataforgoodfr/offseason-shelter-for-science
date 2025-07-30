# Web Scraper Docker - Installation and User Guide

## Directory Structure


```
datagov/asset/                    # Root Directory for Scraping
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

## Quick Installation

### 0. Prerequisites

Make sure you have installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Verify the installation:
```bash
docker --version
docker compose version
```

These different commands must be executed in the project root directory where the docker compose file is located

### 2. Build the Docker image
```bash
docker compose build 
```

### 3. Start the scraping service
```bash
docker compose up
```

### 4. Stop or interrupt the scraping
```bash
docker stop web-scraper-app
```

### 5. Application logs
```bash
docker compose logs web-scraper-app 
```
or
```bash
docker compose logs -f web-scraper-app  # Real-time
```
