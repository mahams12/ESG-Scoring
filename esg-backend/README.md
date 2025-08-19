# ESG Investment Research System - Backend

A comprehensive real-time ESG (Environmental, Social, Governance) investment research platform with AI-powered analysis and multi-source data collection.

## 🚀 Features

### Core Capabilities
- **Real-time Company Validation**: Multi-source validation of publicly traded companies
- **AI-Powered ESG Analysis**: ChatGPT integration for intelligent ESG scoring and insights
- **Multi-Source Data Collection**: Financial, ESG, news, and regulatory data aggregation
- **Industry Benchmarking**: Peer comparison and industry analysis
- **News Sentiment Analysis**: Real-time news monitoring and sentiment scoring
- **Bulk Processing**: Batch analysis of multiple companies
- **RESTful API**: Comprehensive API with proper error handling and validation

### Data Sources
- **Financial**: Financial Modeling Prep, Yahoo Finance, IEX Cloud
- **ESG Ratings**: Sustainalytics, CDP, MSCI ESG, ESG Enterprise
- **News & Sentiment**: NewsAPI, Reddit discussions
- **Regulatory**: EPA enforcement data, OSHA safety records

## 🏗️ Architecture

### Technology Stack
- **Backend Framework**: FastAPI (Python 3.11+)
- **Database**: MongoDB with Motor (async driver)
- **Caching**: Redis for performance optimization
- **AI Integration**: OpenAI GPT-4 for ESG analysis
- **Background Tasks**: Celery with Redis broker
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker & Docker Compose

### Project Structure
```
esg-backend/
├── app/
│   ├── api/routes/          # API endpoint definitions
│   ├── core/                # Core business logic
│   ├── models/              # Pydantic data models
│   ├── services/            # Business logic services
│   ├── utils/               # Utility functions
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connection & operations
│   └── main.py             # FastAPI application entry point
├── tests/                  # Unit and integration tests
├── docker/                 # Docker configuration files
├── logs/                   # Application logs
├── requirements.txt        # Python dependencies
├── config.yaml            # Application configuration
├── docker-compose.yml     # Docker services orchestration
└── Dockerfile             # Container image definition
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- MongoDB 4.4+
- Redis 6.0+
- Docker & Docker Compose (for containerized deployment)

### API Keys Required
- **Financial Modeling Prep**: [Get API Key](https://financialmodelingprep.com/)
- **OpenAI**: [Get API Key](https://openai.com/api/)
- **News API**: [Get API Key](https://newsapi.org/)
- **IEX Cloud**: [Get API Key](https://iexcloud.io/)

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/your-org/esg-backend.git
cd esg-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Start services (MongoDB & Redis)**
```bash
# Using Docker
docker-compose up -d mongo redis

# Or install locally and start services
```

6. **Run the application**
```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python app/main.py
```

7. **Access the API**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health
- API Info: http://localhost:8000/api/v1/info

### Docker Deployment

1. **Using Docker Compose (Recommended)**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

2. **Services Available**
- **ESG API**: http://localhost:8000
- **MongoDB Express**: http://localhost:8081 (admin/admin)
- **Redis Commander**: http://localhost:8082
- **Grafana Dashboard**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090

### Production Deployment

1. **Update environment variables for production**
```bash
export ENVIRONMENT=production
export DEBUG=false
export MONGODB_CONNECTION_STRING="your-production-mongodb-url"
# Update other production settings
```

2. **Use production Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📖 API Documentation

### Core Endpoints

#### Company Validation
```http
POST /api/v1/company/validate
{
  "ticker": "AAPL",
  "force_refresh": false
}
```

#### ESG Analysis
```http
POST /api/v1/analysis/esg
{
  "ticker": "AAPL",
  "include_ai_insights": true,
  "include_benchmarks": true
}
```

#### Health Check
```http
GET /api/v1/health
```

### Response Format
All API responses follow a consistent format:
```json
{
  "status": "success|error|warning",
  "message": "Human readable message",
  "data": { /* Response data */ },
  "errors": [ /* Error details */ ],
  "warnings": [ /* Warning messages */ ],
  "metadata": {
    "processing_time_ms": 1250.5,
    "data_sources_used": ["yahoo_finance", "fmp"],
    "cache_hit": false
  },
  "timestamp": "2025-08-19T10:30:00Z"
}
```

### Error Handling
The API uses standard HTTP status codes and provides detailed error information:

- **400**: Bad Request - Invalid input parameters
- **404**: Not Found - Company or resource not found
- **422**: Validation Error - Request validation failed
- **429**: Rate Limited - Too many requests
- **500**: Internal Error - Server-side error
- **503**: Service Unavailable - External service unavailable

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ENVIRONMENT` | Application environment | No | `development` |
| `DEBUG` | Enable debug mode | No | `false` |
| `MONGODB_CONNECTION_STRING` | MongoDB connection URL | Yes | - |
| `REDIS_HOST` | Redis server host | No | `localhost` |
| `REDIS_PORT` | Redis server port | No | `6379` |
| `FMP_API_KEY` | Financial Modeling Prep API key | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `NEWS_API_KEY` | News API key | Yes | - |
| `IEX_API_KEY` | IEX Cloud API key | Yes | - |

### Configuration File (config.yaml)

The application supports YAML-based configuration for advanced settings:

```yaml
app:
  name: "ESG Investment Research System"
  version: "2.0"
  debug: false

apis:
  financial_modeling_prep:
    rate_limit: 300
    timeout: 30
  
  openai:
    model: "gpt-4"
    max_tokens: 2000
    temperature: 0.3

caching:
  company_validation_ttl: 3600
  financial_data_ttl: 900
  esg_ratings_ttl: 1800
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_company_validator.py

# Run with verbose output
pytest -v
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service integration testing
- **API Tests**: Endpoint testing
- **Performance Tests**: Load and stress testing

### Manual Testing
```bash
# Test company validation
curl -X POST "http://localhost:8000/api/v1/company/validate" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

# Test health check
curl "http://localhost:8000/api/v1/health"
```

## 📊 Monitoring

### Health Checks
- **Liveness**: `/api/v1/health/live`
- **Readiness**: `/api/v1/health/ready`
- **Detailed**: `/api/v1/health/detailed`

### Metrics
- Request/response times
- API success/failure rates
- Database connection status
- External API availability
- Cache hit rates

### Logging
Structured logging with multiple levels:
```python
from loguru import logger

logger.info("Application started")
logger.warning("Cache miss for ticker AAPL")
logger.error("Database connection failed")
```

## 🔒 Security

### Authentication
- API key-based authentication for external services
- Rate limiting per client
- Request validation and sanitization

### Data Protection
- Sensitive data encryption at rest
- Secure API key management
- Input validation and SQL injection prevention

### CORS Configuration
```python
# Configured for specific origins
allow_origins = [
    "http://localhost:3000",
    "https://your-frontend-domain.com"
]
```

## 🚀 Performance

### Optimization Strategies
- **Async Operations**: Non-blocking I/O for all database and API calls
- **Caching**: Redis-based caching for frequently accessed data
- **Connection Pooling**: Optimized database connection management
- **Bulk Operations**: Efficient batch processing for multiple companies

### Scaling
- **Horizontal Scaling**: Multiple API instances behind load balancer
- **Database Sharding**: MongoDB collection sharding for large datasets
- **Caching Layer**: Redis cluster for distributed caching
- **Background Processing**: Celery workers for async tasks

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
```bash
# Check MongoDB status
docker-compose logs mongo

# Verify connection string
echo $MONGODB_CONNECTION_STRING
```

2. **API Key Errors**
```bash
# Verify API keys are set
env | grep API_KEY

# Test API connectivity
curl "https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=YOUR_KEY"
```

3. **Memory Issues**
```bash
# Monitor memory usage
docker stats

# Adjust memory limits in docker-compose.yml
```

### Debug Mode
Enable debug mode for detailed logging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run tests: `pytest`
5. Run linting: `black . && flake8`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push branch: `git push origin feature/amazing-feature`
8. Create Pull Request

### Code Standards
- **Formatting**: Black for code formatting
- **Linting**: Flake8 for code quality
- **Type Hints**: mypy for type checking
- **Documentation**: Comprehensive docstrings
- **Testing**: Minimum 80% test coverage

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♀️ Support

### Documentation
- **API Docs**: Available at `/docs` when running the application
- **Architecture Guide**: See `docs/architecture.md`
- **Deployment Guide**: See `docs/deployment.md`

### Getting Help
- **Issues**: Create GitHub issue for bugs or feature requests
- **Discussions**: Join GitHub discussions for questions
- **Email**: support@esg-research.com

### Changelog
See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

## 🎯 Roadmap

### Version 2.1 (Planned)
- [ ] GraphQL API support
- [ ] Advanced ESG score customization
- [ ] Machine learning models for predictive analysis
- [ ] Real-time WebSocket notifications

### Version 2.2 (Future)
- [ ] Multi-language support
- [ ] Advanced portfolio analysis
- [ ] Integration with more ESG data providers
- [ ] Mobile API optimizations

---

**Built with ❤️ for sustainable investing**