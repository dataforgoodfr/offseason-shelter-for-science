# 🕷️ DataGov Asset Scraper

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://docs.python.org/3/)
[![Scrapy](https://img.shields.io/badge/Scrapy-FF6600?style=for-the-badge&logo=scrapy&logoColor=white)](https://scrapy.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)

The **web scraping engine** for the DataGov Asset Collector. This service crawls government data portals to discover and catalog downloadable climate datasets, providing the raw data for the rescue system.

## 🎯 Purpose

The Asset Scraper is the **crawling component** of the data discovery system, responsible for:

- **🕸️ Web Crawling**: Systematically visiting dataset pages
- **🔗 Link Discovery**: Finding downloadable file links
- **📊 Metadata Extraction**: Collecting file information and sizes
- **🔄 State Management**: Tracking crawling progress with Redis
- **📁 Data Organization**: Structuring scraped data for processing

## 🏗️ Architecture

### **Core Components**
- **Scrapy Framework** for web crawling and scraping
- **Redis Cache** for URL deduplication and state management
- **Docker Containerization** for consistent deployment
- **JSON Pipeline** for data output and processing
- **Progress Tracking** with real-time monitoring

### **Data Flow**
```
Target URLs → Scrapy Spiders → Link Extraction → File Analysis
     ↓            ↓              ↓              ↓
Redis Cache → Progress Tracking → JSON Output → Database Import
```

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Redis](https://redis.io/) for caching (included in Docker setup)
- Python 3.8+ for local development

### 🐳 Docker Setup (Recommended)

1. **Navigate to the asset directory:**
```bash
cd datagov/asset
```

2. **Verify Docker installation:**
```bash
docker --version
docker compose version
```

3. **Build the Docker image:**
```bash
docker compose build
```

4. **Start the scraping service:**
```bash
docker compose up
```

5. **Monitor scraping progress:**
```bash
docker compose logs -f web-scraper-app
```

### 💻 Local Development

1. **Install dependencies:**
```bash
uv sync
```

2. **Start Redis (if not using Docker):**
```bash
redis-server
```

3. **Run the scraper:**
```bash
uv run python main.py
```

## 📁 Project Structure

```
datagov/asset/                    # Root Directory for Scraping
├── 📁 spiders/                   # Scrapy spider definitions
│   └── link_spider.py           # Main link discovery spider
├── 📁 pipelines/                 # Data processing pipelines
│   └── file_info_pipeline.py    # File metadata extraction
├── 📁 output/                    # Scraped data output
├── 📁 logs/                      # Application logs
├── manager.py                    # Scraping orchestration
├── collector.py                  # Collection logic
├── link_scraper.py              # Link extraction utilities
├── redis_cache.py               # Redis caching layer
├── asset.py                     # Asset data model
├── main.py                      # Application entry point
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Container definition
├── requirements.txt             # Python dependencies
└── deploy.sh                    # Deployment script
```

## 🛠️ Development

### **Key Components**

#### **Manager** (`manager.py`)
- **Scrapy process** orchestration
- **Collector coordination**
- **Progress tracking** with tqdm
- **Error handling** and recovery

#### **Link Scraper** (`link_scraper.py`)
- **Web page crawling** logic
- **Link extraction** algorithms
- **File discovery** mechanisms
- **URL validation** and filtering

#### **Redis Cache** (`redis_cache.py`)
- **URL deduplication** to avoid re-scraping
- **Scraping state** management
- **Cache expiration** handling
- **Performance optimization**

#### **Asset Model** (`asset.py`)
- **Data structure** for scraped assets
- **Size calculation** utilities
- **Metadata storage** format
- **Validation methods**

### **Data Processing Pipelines**

#### **File Info Pipeline** (`pipelines/file_info_pipeline.py`)
- **File metadata** extraction
- **Size calculation** from headers
- **Type detection** from URLs
- **Data validation** and cleaning

#### **Spider Implementation** (`spiders/link_spider.py`)
- **Page parsing** logic
- **Link extraction** rules
- **Follow-up requests** management
- **Error handling** for failed pages

## 🔧 Configuration

### **Environment Variables**

Key configuration options:

```bash
# Scraping Configuration
SCRAPER_URL=https://catalog.data.gov
COLLECTION_NAME=climate_data_2024
OUTPUT_FORMAT=json
CONCURRENT_REQUESTS=16
DOWNLOAD_DELAY=1

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_EXPIRY_HOURS=24

# Output Configuration
OUTPUT_DIRECTORY=/app/output
LOG_LEVEL=INFO
```

### **Docker Configuration**

The `docker-compose.yml` includes:
- **Scrapy application** with volume mounting
- **Redis cache** for performance optimization
- **Output directory** for scraped data
- **Log directory** for application logs
- **Network configuration** for service communication

### **Scrapy Settings**

Core Scrapy configuration in `main.py`:

```python
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
}
```

## 📊 Scraping Process

### **Discovery Phase**

1. **URL Queue**: Initialize with target URLs
2. **Redis Check**: Verify URLs haven't been scraped
3. **Page Crawling**: Visit each URL systematically
4. **Link Extraction**: Find downloadable file links

### **Processing Phase**

1. **File Analysis**: Determine file types and sizes
2. **Metadata Collection**: Extract comprehensive information
3. **Data Validation**: Verify URLs and metadata
4. **JSON Output**: Structure data for database import

### **Optimization Features**

- **URL Deduplication**: Avoid re-scraping same URLs
- **Rate Limiting**: Respect server resources
- **Progress Tracking**: Real-time monitoring
- **Error Recovery**: Handle failed requests gracefully

## 🗄️ Data Output

### **JSON Format**

The scraper produces structured JSON output:

```json
{
  "resource_id": "abc123",
  "dataset_title": "Climate Data 2024",
  "organization": "NOAA",
  "assets": [
    {
      "url": "https://data.gov/file.csv",
      "size": 1024000,
      "type": "csv",
      "modified": "2024-01-15T10:30:00Z",
      "name": "climate_data_2024.csv"
    }
  ]
}
```

### **Output Directory Structure**

```
output/
├── climate_data_2024/
│   ├── results.json          # Main scraping results
│   ├── metadata.json         # Additional metadata
│   └── logs/                 # Scraping logs
└── logs/
    └── scraper.log           # Application logs
```

## 🧪 Testing

### **Running Tests**

Execute the test suite:
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest test/test_link_scraper.py

# Run with coverage
uv run pytest --cov=.
```

### **Test Coverage**

The test suite covers:
- **Link extraction** functionality
- **Redis cache** operations
- **Data validation** logic
- **Error handling** scenarios
- **Integration testing** with Scrapy

## 📈 Performance Optimization

### **Caching Strategy**

- **Redis-based** URL deduplication
- **Configurable** cache expiration (24 hours default)
- **Memory-efficient** storage
- **Fast lookup** performance

### **Concurrency Control**

- **Configurable** concurrent requests (16 default)
- **Rate limiting** to respect servers (1 second delay)
- **Connection pooling** for efficiency
- **Error recovery** mechanisms

### **Resource Management**

- **Memory monitoring** during scraping
- **Disk space** management for output
- **Network bandwidth** optimization
- **CPU utilization** balancing

## 🐛 Troubleshooting

### **Common Issues**

**Scraping failures:**
- Check network connectivity
- Verify target URLs are accessible
- Review rate limiting settings
- Check Redis connection

**Memory issues:**
- Reduce concurrent requests
- Increase Redis memory limits
- Monitor output directory size
- Check for memory leaks

**Data quality problems:**
- Validate JSON output format
- Check URL accessibility
- Verify metadata completeness
- Review error logs

### **Debugging**

Enable debug mode:
```bash
# Set debug environment variable
export LOG_LEVEL=DEBUG

# Run with verbose output
uv run python main.py --verbose

# Check Redis cache
redis-cli keys "*"
```

### **Service Management**

**Stop the scraping service:**
```bash
docker stop web-scraper-app
```

**View application logs:**
```bash
# All logs
docker compose logs web-scraper-app

# Real-time logs
docker compose logs -f web-scraper-app

# Recent logs
docker compose logs --tail=100 web-scraper-app
```

## 🔐 Security Considerations

### **Rate Limiting**

- **Respectful scraping** practices
- **Configurable delays** between requests
- **User agent** identification
- **Robots.txt** compliance

### **Data Privacy**

- **No personal data** collection
- **Public datasets** only
- **Metadata only** scraping
- **Secure storage** practices

## 📚 Documentation

### **Scrapy Resources**

- **Official Documentation**: https://docs.scrapy.org/
- **Best Practices**: https://docs.scrapy.org/en/latest/topics/practices.html
- **Middleware Development**: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html

### **Redis Resources**

- **Official Documentation**: https://redis.io/documentation
- **Python Client**: https://redis-py.readthedocs.io/
- **Best Practices**: https://redis.io/topics/optimization

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests for new functionality**
5. **Update documentation**
6. **Submit a pull request**

## 📄 License

This project is part of the Offseason Shelter for Science system and is licensed under the MIT License.

---

**Built with ❤️ by Data For Science, for climate data preservation** 🌍
