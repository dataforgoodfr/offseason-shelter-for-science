# 🏠 Offseason Shelter for Science

A **distributed data rescue system** designed to preserve and manage climate data from data.gov (the US government's open data portal). This project creates a resilient infrastructure for storing and managing climate datasets that might be at risk of being lost or becoming inaccessible.

## 🎯 Project Overview

The "Offseason Shelter for Science" is a microservices-based platform that enables distributed data rescue operations. It provides intelligent prioritization, automated discovery, and resilient storage for climate datasets from government open data portals.

### 🌟 Key Features

- **🔍 Automated Data Discovery**: Scrapes and catalogs datasets from CKAN-based portals
- **⚡ Intelligent Prioritization**: Dynamic priority system for dataset rescue order
- **🔄 Distributed Processing**: Multi-node architecture for scalable data rescue
- **💾 Resilient Storage**: PostgreSQL database with proper relationships and indexing
- **📊 Real-time Monitoring**: API endpoints for system status and progress tracking
- **🐳 Containerized Deployment**: Docker-based microservices architecture

## 🏗️ Architecture

The project consists of four main microservices, each running in Docker containers:

### 📊 **Rescue DB** - Central Database Service
- **Purpose**: Manages the catalog of datasets, resources, and assets
- **Technology**: PostgreSQL + FastAPI + SQLAlchemy
- **Key Entities**: Datasets, Resources, Assets, Organizations, AssetKinds
- **Port**: 8000

### 🕷️ **DataGov Asset Collector** - Data Ingestion Service
- **Purpose**: Discovers and catalogs downloadable assets from data.gov
- **Technology**: Scrapy + Redis + CKAN API
- **Features**: Web scraping, metadata extraction, caching
- **Process**: Queries CKAN API → Scrapes dataset pages → Extracts file metadata

### 📡 **Dispatcher** - Task Distribution Service
- **Purpose**: Coordinates allocation of data rescue tasks across nodes
- **Technology**: FastAPI
- **Functionality**: Task distribution, resource management
- **Port**: 8001

### 🎯 **Priorizer** - Intelligent Task Prioritization Service
- **Purpose**: Manages dataset rescue priorities and resource allocation
- **Technology**: FastAPI + APScheduler
- **Features**: Dynamic priority scoring, automatic updates, resource matching
- **API**: Allocation, release, priority updates, status monitoring

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/engine/install/) and Docker Compose
- [UV](https://docs.astral.sh/uv/) (modern Python package manager)

### Running the Services

Each service can be run independently using Docker Compose:

```bash
# Start the Rescue DB (database + API)
cd rescue_db
docker compose up

# Start the Dispatcher service
cd dispatcher
docker compose up

# Start the Priorizer service
cd priorizer
docker compose up

# Start the DataGov Asset Collector
cd datagov/asset
docker compose up
```

### Development Mode

For development, you can run services locally:

```bash
# Rescue DB API
cd rescue_db
uv run fastapi dev rescue_api/main.py

# Dispatcher API
cd dispatcher
uv run fastapi dev api/dispatcher_service.py

# Priorizer API
cd priorizer
uv run fastapi dev main.py
```

## 📡 API Endpoints

### Rescue DB API
- **URL**: http://localhost:8000/docs
- **Purpose**: Database management and dataset catalog

### Dispatcher API
- **URL**: http://localhost:8001/docs
- **Purpose**: Task distribution and coordination

### Priorizer API
- **URL**: http://localhost:8002/docs (default)
- **Endpoints**:
  - `POST /allocate` - Assign datasets to nodes
  - `POST /release` - Release completed datasets
  - `POST /update-ckan` - Update dataset priorities
  - `GET /status` - System status and statistics

## 🔄 Data Flow

1. **🔍 Discovery**: DataGov collector queries CKAN API and scrapes dataset pages
2. **📝 Cataloging**: Metadata is extracted and stored in Rescue DB
3. **🎯 Prioritization**: Priorizer assigns and adjusts priority scores
4. **📦 Distribution**: Dispatcher allocates work to available nodes
5. **💾 Storage**: Nodes download and store assigned datasets
6. **📊 Monitoring**: System tracks progress and provides status updates

## 🛠️ Development

### Database Migrations

```bash
cd rescue_db
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "Description of changes"
```

### Testing

```bash
# Run dispatcher tests
python test/dispatcher/test_dispatcher.py

# Run datagov tests
python test/datagov/ckan/test_resource.py
```

## 🔧 Configuration

Each service has its own configuration:

- **Environment Variables**: Copy `.env.dist` to `.env` and configure
- **Docker Compose**: Service-specific configurations in each directory
- **Database**: PostgreSQL with configurable credentials and database name

## 📁 Project Structure

```
offseason-shelter-for-science/
├── 📊 rescue_db/          # Central database and API
├── 🕷️ datagov/            # Data collection and scraping
├── 📡 dispatcher/         # Task distribution service
├── 🎯 priorizer/          # Priority management service
└── 🧪 test/              # Test suites
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For questions or issues, please check the individual service README files or create an issue in the repository.

---

**Built with ❤️ by Data For Science, for climate data preservation**