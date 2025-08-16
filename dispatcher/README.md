# 📡 Dispatcher

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://docs.python.org/3/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

The **task distribution service** for the Offseason Shelter for Science climate data rescue system. This service coordinates the allocation of data rescue tasks across different nodes and servers, ensuring efficient distribution of climate data rescue operations.

## 🎯 Purpose

The Dispatcher service acts as the **coordinator** in the data rescue ecosystem, responsible for:

- **📦 Task Distribution**: Allocating data rescue jobs to available nodes
- **🔄 Load Balancing**: Ensuring even distribution of work across the network
- **📊 Resource Management**: Tracking node availability and capacity
- **🛡️ Fault Tolerance**: Handling node failures and task reassignment
- **📈 Performance Monitoring**: Tracking rescue progress and efficiency

## 🏗️ Architecture

### **Core Components**
- **FastAPI** for RESTful API endpoints
- **Mock data system** for development and testing
- **JSON-based configuration** for task definitions
- **Health monitoring** for service status

### **Service Integration**
```
Nodes ←→ Dispatcher ←→ Priorizer
  ↓         ↓           ↓
Rescue DB ←→ Status ←→ Monitoring
```

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/engine/install/) and Docker Compose
- [uv](https://docs.astral.sh/uv/) for Python package management (development)
- Python 3.8+ for local development

### 🐳 Docker Setup (Recommended)

1. **Navigate to the project:**
```bash
cd dispatcher
```

2. **Start the service:**
```bash
docker compose up
```

3. **Access the API:**
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

### 💻 Local Development

1. **Install dependencies:**
```bash
uv sync
```

2. **Start the development server:**
```bash
uv run fastapi dev api/dispatcher_service.py
```

3. **Or run with uvicorn:**
```bash
uv run uvicorn api.dispatcher_service:app --reload --port 8001
```

### 🚀 Quick Development Script

Use the provided development script:
```bash
bash -v ./run_docker_dev.sh
```

## 📡 API Endpoints

### **🏠 Root Endpoint**

#### `GET /`
Returns a welcome message for the dispatcher service.

**Response:**
```json
"Hello rescuer 👋"
```

### **📦 Mock Dispatch**

#### `POST /mock_dispatch`
Processes dispatch requests using mock data for development and testing.

**Request:**
```json
{
  "node_id": "node-123",
  "capacity_gb": 100,
  "priority_level": "high"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Payload received and processed",
  "received_data": {
    "node_id": "node-123",
    "capacity_gb": 100,
    "priority_level": "high"
  },
  "mock_data": {
    "assigned_tasks": [
      {
        "task_id": "task-001",
        "dataset_url": "https://data.gov/climate/2024",
        "size_mb": 500,
        "priority": 8
      }
    ],
    "estimated_duration": "2 hours",
    "node_status": "active"
  }
}
```

## 🛠️ Development

### **Project Structure**
```
dispatcher/
├── 📁 api/                   # FastAPI application
│   ├── 📁 mock/             # Mock data for testing
│   │   └── mock_data.json   # Sample response data
│   ├── 📁 models/           # Pydantic data models
│   │   └── payload.py       # Request/response schemas
│   ├── 📁 routers/          # API endpoint definitions
│   │   └── dispatch.py      # Main dispatch endpoints
│   └── dispatcher_service.py # FastAPI application entry
├── docker-compose.yml        # Docker configuration
├── Dockerfile               # Container definition
├── pyproject.toml           # Project dependencies
└── run_docker_dev.sh        # Development script
```

### **Key Components**

#### **API Service** (`api/dispatcher_service.py`)
- **FastAPI application** setup
- **Router registration**
- **Middleware configuration**
- **Error handling**

#### **Dispatch Router** (`api/routers/dispatch.py`)
- **Endpoint definitions**
- **Request processing**
- **Mock data integration**
- **Response formatting**

#### **Data Models** (`api/models/payload.py`)
- **Request validation** schemas
- **Response models**
- **Data type definitions**

### **Mock Data System**

The service includes a comprehensive mock data system for development:

- **Realistic test data** for various scenarios
- **Configurable responses** for different use cases
- **Error simulation** for testing edge cases
- **Performance testing** data

## 🧪 Testing

### **Running Tests**

Execute the test suite:
```bash
python test/dispatcher/test_dispatcher.py
```

### **Test Coverage**

The test suite covers:
- **API endpoint** functionality
- **Request/response** validation
- **Mock data** integration
- **Error handling** scenarios
- **Service integration** testing

### **Test Data**

Test data is located in:
- `api/mock/mock_data.json` - Sample responses
- `test/dispatcher/` - Test scripts and fixtures

## 🔧 Configuration

### **Environment Variables**

Key configuration options:

```bash
# API Configuration
DISPATCHER_HOST=0.0.0.0
DISPATCHER_PORT=8001

# Development
DEBUG=true
LOG_LEVEL=INFO

# Mock Data
MOCK_DATA_PATH=./api/mock/mock_data.json
ENABLE_MOCK_MODE=true
```

### **Docker Configuration**

The `docker-compose.yml` includes:
- **FastAPI application** with hot reload
- **Port mapping** for external access
- **Volume mounting** for development
- **Health checks** for monitoring

### **Development Script**

The `run_docker_dev.sh` script provides:
- **Automatic setup** for development environment
- **Docker container** management
- **Log monitoring** and debugging
- **Quick restart** capabilities

## 📊 Monitoring and Logging

### **Health Checks**

Monitor service health:
```bash
# Check service status
curl http://localhost:8001/health

# View service logs
docker compose logs dispatcher-rescue-api
```

### **Log Levels**

Configure logging verbosity:
- **DEBUG**: Detailed development information
- **INFO**: General operational messages
- **WARNING**: Potential issues
- **ERROR**: Service errors and failures

## 🔄 Integration with Other Services

### **Priorizer Integration**
- **Task allocation** coordination
- **Priority-based** distribution
- **Resource matching** algorithms

### **Rescue DB Integration**
- **Dataset metadata** retrieval
- **Asset information** lookup
- **Progress tracking** updates

### **Node Communication**
- **Capacity reporting** from nodes
- **Task assignment** to nodes
- **Status monitoring** of nodes

## 🐛 Troubleshooting

### **Common Issues**

**Service not starting:**
- Check Docker installation: `docker --version`
- Verify port availability: `netstat -tulpn | grep 8001`
- Check container logs: `docker compose logs dispatcher-rescue-api`

**API not responding:**
- Verify service is running: `docker compose ps`
- Check API documentation: http://localhost:8001/docs
- Review application logs for errors

**Mock data issues:**
- Verify mock data file exists: `ls api/mock/mock_data.json`
- Check JSON format validity
- Ensure file permissions are correct

### **Debugging**

Enable debug mode:
```bash
# Set debug environment variable
export DEBUG=true

# Restart service with debug logging
docker compose restart dispatcher-rescue-api
```

## 🔐 Security Considerations

### **Development Mode**

Current implementation is designed for development:
- **No authentication** required
- **Mock data** for testing
- **Debug logging** enabled
- **CORS** configured for local development

### **Production Recommendations**

For production deployment:
- **🔑 Authentication**: Implement API key or JWT
- **🛡️ Rate Limiting**: Prevent API abuse
- **🔐 HTTPS**: Secure communication
- **📊 Monitoring**: Add metrics and alerting
- **🔄 Load Balancing**: Multiple service instances

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