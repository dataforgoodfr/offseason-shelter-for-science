# 📊 Rescue DB

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://docs.python.org/3/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

The **central database service** for the Offseason Shelter for Science climate data rescue system. This service manages the catalog of datasets, resources, and assets from data.gov, providing a comprehensive database for tracking and organizing climate data that needs to be preserved.

## 🎯 Purpose

Rescue DB serves as the **single source of truth** for all climate data metadata in the rescue system. It stores information about:

- **📋 Datasets**: Complete metadata from data.gov (title, description, organization, access statistics)
- **📁 Resources**: Individual data sources within datasets (files, APIs, databases)
- **💾 Assets**: Actual downloadable files with URLs, sizes, and metadata
- **🏢 Organizations**: Government agencies that publish the data
- **📄 AssetKinds**: Types of files (CSV, JSON, ZIP, etc.)

## 🏗️ Architecture

### **Database Schema**
- **PostgreSQL** with SQLAlchemy ORM
- **Alembic** for database migrations
- **Proper relationships** between all entities
- **Indexing** for optimal query performance

### **API Layer**
- **FastAPI** for RESTful API endpoints
- **Automatic documentation** at `/docs`
- **Pydantic models** for request/response validation
- **Database connection pooling**

## 🚀 Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python package management
- [Docker Compose](https://docs.docker.com/compose/) for containerized deployment
- [PostgreSQL](https://www.postgresql.org/) (included in Docker setup)

### 🐳 Docker Setup (Recommended)

1. **Clone and navigate to the project:**
```bash
cd rescue_db
```

2. **Configure environment:**
```bash
cp .env.dist .env
# Edit .env with your database credentials
```

3. **Start the services:**
```bash
docker compose up
```

4. **Access the API:**
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

### 💻 Local Development

1. **Install dependencies:**
```bash
uv sync
```

2. **Set up environment:**
```bash
cp .env.dist .env
# Configure your local PostgreSQL connection
```

3. **Run database migrations:**
```bash
uv run alembic upgrade head
```

4. **Start the development server:**
```bash
uv run fastapi dev rescue_api/main.py
```

## 📡 API Endpoints

### **Core Endpoints**
- `GET /datasets` - List all datasets
- `GET /datasets/{id}` - Get specific dataset details
- `GET /resources` - List all resources
- `GET /assets` - List all downloadable assets
- `GET /organizations` - List all organizations

### **Search & Filter**
- `GET /datasets/search` - Search datasets by criteria
- `GET /assets/by-type` - Filter assets by file type
- `GET /datasets/by-organization` - Filter by organization

### **Statistics**
- `GET /stats/overview` - System overview statistics
- `GET /stats/organizations` - Data distribution by organization
- `GET /stats/file-types` - Asset distribution by file type

## 🗄️ Database Management

### **Migrations**

Apply the latest migrations:
```bash
uv run alembic upgrade head
```

Create a new migration:
```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

### **Database Models**

Key entities in the system:

- **`Dataset`**: Core dataset information from data.gov
- **`Resource`**: Individual data sources within datasets
- **`Asset`**: Actual downloadable files with metadata
- **`Organization`**: Government agencies publishing data
- **`AssetKind`**: File type classifications

### **Relationships**
```
Organization → Datasets → Resources → Assets
                    ↓
                AssetKinds
```

## 🛠️ Development

### **Project Structure**
```
rescue_db/
├── 📁 rescue_api/           # FastAPI application
│   ├── 📁 entities/         # SQLAlchemy models
│   ├── 📁 models/           # Pydantic schemas
│   ├── 📁 routers/          # API endpoints
│   └── main.py             # Application entry point
├── 📁 alembic/             # Database migrations
├── 📁 manual_data_update/  # Manual data operations
└── docker-compose.yml      # Docker configuration
```

### **Adding New Models**

1. **Create the model** in `rescue_api/entities/`
2. **Generate migration:**
```bash
uv run alembic revision --autogenerate -m "Add new model"
```
3. **Review and apply migration:**
```bash
uv run alembic upgrade head
```

### **Testing**

Run the test suite:
```bash
uv run pytest
```

## 🔧 Configuration

### **Environment Variables**

Key configuration options in `.env`:

```bash
# Database
RESCUE_API_POSTGRES_USER=user
RESCUE_API_POSTGRES_PASSWORD=password
RESCUE_API_POSTGRES_DB=us_climate_data

# API
RESCUE_API_HOST=0.0.0.0
RESCUE_API_PORT=80

# Development
RESCUE_API_DEBUG=true
```

### **Docker Configuration**

The `docker-compose.yml` includes:
- **PostgreSQL database** with health checks
- **FastAPI application** with hot reload
- **Volume persistence** for database data
- **Network isolation** for security

## 📊 Data Operations

### **Manual Data Updates**

The `manual_data_update/` directory contains scripts for:
- **Data deduplication** operations
- **Bulk data imports** and updates
- **Data validation** and cleanup
- **Performance optimization** scripts

### **Backup and Recovery**

```bash
# Create database backup
docker exec rescue_db_db_1 pg_dump -U user us_climate_data > backup.sql

# Restore from backup
docker exec -i rescue_db_db_1 psql -U user us_climate_data < backup.sql
```

## 🐛 Troubleshooting

### **Common Issues**

**Database connection failed:**
- Check PostgreSQL is running
- Verify credentials in `.env`
- Ensure port 5432 is available

**Migration errors:**
- Check for conflicting migrations
- Verify model changes are correct
- Review migration files before applying

**API not responding:**
- Check FastAPI logs
- Verify port 8000 is available
- Ensure all dependencies are installed

### **Logs**

View application logs:
```bash
# Docker logs
docker compose logs rescue-api

# Database logs
docker compose logs db
```

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
