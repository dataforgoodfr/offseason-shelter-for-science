# 🎯 Priorizer

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://docs.python.org/3/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![APScheduler](https://img.shields.io/badge/APScheduler-FF6B6B?style=for-the-badge&logo=python&logoColor=white)](https://apscheduler.readthedocs.io/)

The **intelligent task prioritization service** for the Offseason Shelter for Science climate data rescue system. This service manages dataset rescue priorities, allocates resources to nodes, and ensures the most important climate data is rescued first.

## 🎯 Purpose

The Priorizer service is the **brain** of the data rescue operation, making intelligent decisions about:

- **📊 Priority Scoring**: Assigning importance levels (1-10) to datasets
- **🔄 Dynamic Updates**: Automatically adjusting priorities based on system state
- **📦 Resource Allocation**: Matching datasets to available storage space
- **⏰ Task Scheduling**: Managing the rescue queue efficiently
- **📈 System Monitoring**: Tracking rescue progress and statistics

## 🏗️ Architecture

### **Core Components**
- **FastAPI** for RESTful API endpoints
- **APScheduler** for automated priority updates
- **JSON-based storage** for allocations and priorities
- **Background processing** for continuous optimization

### **Data Flow**
```
CKAN Data → Priority Scoring → Resource Matching → Node Allocation
     ↓              ↓              ↓              ↓
JSON Storage → Auto Updates → Status Monitoring → API Responses
```

## 🚀 Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python package management
- [Docker Compose](https://docs.docker.com/compose/) for containerized deployment
- Python 3.8+ for local development

### 🐳 Docker Setup (Recommended)

1. **Navigate to the project:**
```bash
cd priorizer
```

2. **Start the service:**
```bash
docker compose up
```

3. **Access the API:**
- **API Documentation**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/health

### 💻 Local Development

1. **Install dependencies:**
```bash
uv sync
```

2. **Start the development server:**
```bash
uv run fastapi dev main.py
```

3. **Or run with uvicorn:**
```bash
uv run uvicorn main:app --reload --port 8002
```

## 📡 API Endpoints

### **🎯 Asset Allocation**

#### `POST /allocate`
Allocates datasets to a node based on available storage space.

**Request:**
```json
{
  "free_space_gb": 10,
  "node_id": "node-123"
}
```

**Response:**
```json
[
  {
    "id": "asset-1",
    "url": "https://data.gov/file1.zip",
    "size_mb": 500,
    "priority": 8,
    "name": "climate_data_2024.zip"
  }
]
```

### **🔄 Asset Release**

#### `POST /release`
Releases a previously allocated asset.

**Request:**
```json
{
  "asset_id": "asset-1",
  "node_id": "node-123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Asset released successfully"
}
```

### **⚙️ Priority Management**

#### `POST /update-ckan`
Manually updates dataset priorities.

**Request:**
```json
{
  "updates": [
    {
      "asset_id": "asset-1",
      "new_priority": 9
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "updated_items": 1
}
```

### **📊 System Status**

#### `GET /status`
Returns global system status and statistics.

**Response:**
```json
{
  "ckan_datasets": 1250,
  "active_allocations": 15,
  "next_auto_update": "2025-01-15T14:30:00",
  "total_priority_score": 8750,
  "system_health": "healthy"
}
```

## 🔄 Automated Priority Updates

The service runs a **BackgroundScheduler** that performs automatic maintenance every 2 minutes:

### **🔄 Priority Adjustments**
- **Random variations** (±1) to prevent stagnation
- **Range enforcement** (1-10 priority scale)
- **Load balancing** across different priority levels

### **🧹 Cleanup Operations**
- **Expired allocations** (> 24 hours) are automatically released
- **Orphaned assets** are returned to the available pool
- **System statistics** are updated

### **📈 Optimization**
- **Priority distribution** analysis
- **Resource utilization** tracking
- **Performance metrics** collection

## 🛠️ Development

### **Project Structure**
```
priorizer/
├── 📁 dispatcher/           # Core business logic
│   ├── logic.py            # Allocation and priority logic
│   └── schemas.py          # Pydantic data models
├── 📁 data/                # JSON data storage
│   ├── allocations.json    # Active allocations
│   └── ckan_data.json      # Dataset priorities
├── main.py                 # FastAPI application
├── docker-compose.yml      # Docker configuration
└── pyproject.toml          # Project dependencies
```

### **Key Components**

#### **Dispatcher Logic** (`dispatcher/logic.py`)
- **Asset allocation** algorithms
- **Priority calculation** methods
- **Resource matching** logic
- **Data persistence** operations

#### **Data Schemas** (`dispatcher/schemas.py`)
- **Request/Response** models
- **Data validation** rules
- **API documentation** generation

### **Adding New Features**

1. **Update schemas** in `dispatcher/schemas.py`
2. **Implement logic** in `dispatcher/logic.py`
3. **Add endpoints** in `main.py`
4. **Update tests** in `tests/`
5. **Update documentation**

## 🔧 Configuration

### **Environment Variables**

Key configuration options:

```bash
# API Configuration
PRIORIZER_HOST=0.0.0.0
PRIORIZER_PORT=8002

# Scheduling
AUTO_UPDATE_INTERVAL_MINUTES=2
ALLOCATION_EXPIRY_HOURS=24

# Data Storage
DATA_DIRECTORY=./data
ALLOCATIONS_FILE=allocations.json
CKAN_DATA_FILE=ckan_data.json

# Development
DEBUG=true
LOG_LEVEL=INFO
```

### **Docker Configuration**

The `docker-compose.yml` includes:
- **FastAPI application** with hot reload
- **Volume mounting** for data persistence
- **Health checks** for monitoring
- **Network configuration** for service communication

## 📊 Data Management

### **JSON Storage**

The service uses JSON files for data persistence:

- **`allocations.json`**: Active asset allocations to nodes
- **`ckan_data.json`**: Dataset metadata with priority scores

### **Data Backup**

```bash
# Backup data files
cp data/allocations.json data/allocations.json.backup
cp data/ckan_data.json data/ckan_data.json.backup

# Restore from backup
cp data/allocations.json.backup data/allocations.json
cp data/ckan_data.json.backup data/ckan_data.json
```

## 🐛 Troubleshooting

### **Common Issues**

**Service not responding:**
- Check if the service is running: `docker compose ps`
- View logs: `docker compose logs priorizer`
- Verify port availability: `netstat -tulpn | grep 8002`

**Priority updates not working:**
- Check scheduler status in logs
- Verify JSON file permissions
- Ensure data files are readable/writable

**Allocation failures:**
- Check available datasets in `ckan_data.json`
- Verify node storage requirements
- Review allocation logic in logs

### **Logs and Monitoring**

View service logs:
```bash
# Docker logs
docker compose logs priorizer

# Follow logs in real-time
docker compose logs -f priorizer

# Check specific log levels
docker compose logs priorizer | grep ERROR
```

## 🔐 Security Considerations

### **Production Recommendations**

For production deployment, consider:

- **🔑 Authentication**: Add API key or JWT authentication
- **🗄️ Database**: Replace JSON files with PostgreSQL/MongoDB
- **🔒 Concurrency**: Implement file locking or database transactions
- **📊 Monitoring**: Add metrics collection and alerting
- **🛡️ Rate Limiting**: Prevent API abuse
- **🔐 HTTPS**: Secure API communication

### **Current Limitations**

- **File-based storage** (not suitable for high concurrency)
- **No authentication** (development only)
- **Limited scalability** (single instance)
- **Manual backup** required

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