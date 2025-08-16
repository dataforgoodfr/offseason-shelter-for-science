# 🕷️ DataGov Asset Collector

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://docs.python.org/3/)
[![Scrapy](https://img.shields.io/badge/Scrapy-FF6600?style=for-the-badge&logo=scrapy&logoColor=white)](https://scrapy.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![CKAN](https://img.shields.io/badge/CKAN-7D3C98?style=for-the-badge&logo=ckan&logoColor=white)](https://ckan.org/)

The **data ingestion and discovery service** for the Offseason Shelter for Science climate data rescue system. This service scrapes and catalogs downloadable assets from data.gov and other CKAN-based portals, providing the foundation for climate data rescue operations.

## 🎯 Purpose

The DataGov Asset Collector is the **discovery engine** of the data rescue system, responsible for:

- **🔍 Data Discovery**: Finding climate datasets across government portals
- **📊 Metadata Extraction**: Collecting comprehensive dataset information
- **💾 Asset Cataloging**: Identifying downloadable files and resources
- **🔄 Continuous Monitoring**: Tracking new and updated datasets
- **📈 Data Intelligence**: Analyzing dataset popularity and access patterns

## 🏗️ Architecture

### **Core Components**
- **Scrapy Framework** for web scraping and crawling
- **CKAN API Integration** for structured data access
- **Redis Caching** for performance optimization
- **JSON Pipeline** for data processing and storage
- **Docker Containerization** for deployment

### **Data Flow**
```
CKAN API → Scrapy Spiders → Asset Discovery → Metadata Extraction
    ↓           ↓              ↓                ↓
Redis Cache → File Processing → JSON Storage → Database Import
```

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/engine/install/) and Docker Compose
- [Redis](https://redis.io/) for caching (included in Docker setup)
- Python 3.8+ for local development

### 🐳 Docker Setup (Recommended)

1. **Navigate to the asset directory:**
```bash
cd datagov/asset
```

2. **Start the services:**
```bash
docker compose up
```

3. **Monitor scraping progress:**
```bash
docker compose logs -f asset-collector
```

### 💻 Local Development

1. **Install dependencies:**
```bash
cd datagov/asset
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

## 📡 API Integration

### **CKAN API**

The service integrates with the data.gov CKAN API for structured data access.

**Base URL**: https://catalog.data.gov/api/3/

**Example Query:**
```bash
curl -X POST "https://catalog.data.gov/api/3/action/package_search" \
     -H "Content-Type: application/json" \
     -d '{"fq": "organization:\"census-gov\""}' | json_pp
```

**Key Endpoints:**
- `package_search` - Search for datasets
- `package_show` - Get dataset details
- `resource_show` - Get resource information
- `organization_list` - List organizations

### **NOCODB API** (Legacy)

For legacy data management systems:

**Insert Records:**
```bash
curl --request POST \
    --url 'https://NOCODB_DOMAIN/api/v2/tables/TABLE_ID/records' \
    --header 'xc-token: <TOKEN>' \
    --header 'Content-Type: application/json' \
    --data '[{"foo": "Foo bar", "bar": "2025-05-30", "unknown_field": "ERROR!"}, {"foo": "bar", "bar": "2025-05-31", "unknown_field": "?"}]'
```

## 🛠️ Development

### **Project Structure**
```
datagov/
├── 📁 asset/                 # Main scraping service
│   ├── 📁 pipelines/         # Data processing pipelines
│   │   ├── file_info_pipeline.py
│   │   └── json_pipelines.py
│   ├── 📁 spiders/           # Scrapy spiders
│   │   ├── link_spider.py
│   │   └── web_directory.py
│   ├── 📁 output/            # Scraped data output
│   ├── asset.py              # Asset data model
│   ├── collector.py          # Collection logic
│   ├── link_scraper.py       # Link extraction
│   ├── manager.py            # Scraping manager
│   ├── redis_cache.py        # Redis caching
│   └── main.py               # Entry point
├── 📁 ckan/                  # CKAN API integration
│   ├── package_search.py     # Dataset search
│   └── model_manager.py      # Data model management
├── asset_to_db.py            # Database import
├── asset_retrieval.py        # Asset retrieval logic
├── json_to_db.py             # JSON to database
├── json_to_tabular.py        # Data conversion
└── url_mapping_builder.py    # URL mapping utilities
```

### **Key Components**

#### **Asset Manager** (`asset/manager.py`)
- **Scrapy process** management
- **Collector coordination**
- **Progress tracking**
- **Error handling**

#### **Link Scraper** (`asset/link_scraper.py`)
- **Web page crawling**
- **Link extraction**
- **File discovery**
- **URL validation**

#### **Redis Cache** (`asset/redis_cache.py`)
- **URL deduplication**
- **Scraping state** management
- **Performance optimization**
- **Cache expiration**

#### **CKAN Integration** (`ckan/package_search.py`)
- **API communication**
- **Dataset search**
- **Metadata extraction**
- **Pagination handling**

### **Data Processing Pipelines**

#### **File Info Pipeline** (`pipelines/file_info_pipeline.py`)
- **File metadata** extraction
- **Size calculation**
- **Type detection**
- **URL validation**

#### **JSON Pipelines** (`pipelines/json_pipelines.py`)
- **Data serialization**
- **Format conversion**
- **Output management**
- **Error handling**

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
- **Redis cache** for performance
- **Output directory** for scraped data
- **Network configuration** for service communication

## 📊 Data Collection Process

### **Discovery Phase**

1. **CKAN API Query**: Search for climate-related datasets
2. **Organization Filtering**: Focus on relevant government agencies
3. **Dataset Enumeration**: Collect all available datasets
4. **Resource Identification**: Find downloadable assets

### **Scraping Phase**

1. **Page Crawling**: Visit dataset pages
2. **Link Extraction**: Find download links
3. **File Analysis**: Determine file types and sizes
4. **Metadata Collection**: Extract comprehensive information

### **Processing Phase**

1. **Data Validation**: Verify URLs and metadata
2. **Deduplication**: Remove duplicate entries
3. **Categorization**: Classify by file type and organization
4. **Storage**: Save to JSON format for database import

## 🗄️ Data Storage

### **Output Formats**

The service produces structured JSON data:

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
      "modified": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### **Database Integration**

Use the provided scripts to import data:

```bash
# Import assets to database
python asset_to_db.py /path/to/scraped/data

# Convert JSON to tabular format
python json_to_tabular.py input.json output.csv

# Build URL mappings
python url_mapping_builder.py
```

## 🧪 Testing

### **Running Tests**

Execute the test suite:
```bash
# Test CKAN integration
python test/datagov/ckan/test_resource.py

# Test asset processing
python -m pytest test/datagov/
```

### **Test Coverage**

The test suite covers:
- **CKAN API** integration
- **Asset processing** pipelines
- **Data validation** logic
- **Cache operations**
- **Error handling** scenarios

## 📈 Performance Optimization

### **Caching Strategy**

- **Redis-based** URL deduplication
- **Configurable** cache expiration
- **Memory-efficient** storage
- **Fast lookup** performance

### **Concurrency Control**

- **Configurable** concurrent requests
- **Rate limiting** to respect servers
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

### **CKAN API Resources**

- **User Guide**: https://data.gov/user-guide/#data-gov-ckan-api
- **API Documentation**: https://docs.ckan.org/en/latest/api/
- **GitHub Repository**: https://github.com/ckan/ckanapi

### **Scrapy Resources**

- **Official Documentation**: https://docs.scrapy.org/
- **Best Practices**: https://docs.scrapy.org/en/latest/topics/practices.html
- **Middleware Development**: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html

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