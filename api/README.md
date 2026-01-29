# SAR Submission API

Production-ready FastAPI service for submitting and validating Suspicious Activity Reports (SARs).

## Features

- ✅ **JWT Authentication**: Bearer token auth with scope validation
- ✅ **Request Validation**: Integration with existing `sar_parser` validator
- ✅ **Database Persistence**: PostgreSQL with SQLAlchemy ORM
- ✅ **Idempotency**: Duplicate submission handling via idempotency keys
- ✅ **Rate Limiting**: Configurable request throttling with Redis
- ✅ **Structured Logging**: JSON logs with correlation IDs
- ✅ **Observability**: Prometheus metrics + health endpoints
- ✅ **Security**: TLS termination, input validation, scope-based authorization
- ✅ **Docker Support**: Full stack with docker-compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)

### Running with Docker Compose

```bash
# Generate SSL certificates for local development
cd docker/nginx
./generate_ssl.sh
cd ../..

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Run database migrations
docker-compose -f docker/docker-compose.yml exec api alembic upgrade head

# Check health
curl -k https://localhost/health
```

### Local Development

```bash
# Install dependencies
pip install -r requirements/dev.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start the API
uvicorn api.main:app --reload --port 8000

# In another terminal, run tests
pytest tests/ -v
```

## API Documentation

Once the API is running, visit:
- **Interactive Docs**: https://localhost/docs
- **OpenAPI Schema**: https://localhost/openapi.json

## Usage

### Generate a JWT Token

```bash
python tools/generate_jwt.py --subject "user@example.com" --scope "sar:write" --hours 1
```

### Submit a SAR Record

```bash
export JWT_TOKEN="<your-token-here>"

curl -X POST https://localhost/api/sar-records \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filing_type": "Initial",
    "filing_date": "2024-05-01",
    "filer_name": "Example Financial Institution",
    "filer_address": {
      "address_line1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "US"
    },
    "subjects": [
      {
        "name": "John Doe",
        "entity_type": "Individual"
      }
    ],
    "transactions": [
      {
        "date": "2024-04-30",
        "amount": "1000.50",
        "currency": "USD"
      }
    ]
  }' | jq
```

## Project Structure

```
api/
├── main.py                  # FastAPI application entry point
├── config.py                # Configuration management
├── models/
│   ├── database.py          # SQLAlchemy models
│   └── schemas.py           # Pydantic request/response models
├── routes/
│   ├── sar_records.py       # POST /api/sar-records endpoint
│   └── health.py            # Health/readiness endpoints
├── middleware/
│   ├── auth.py              # JWT bearer token validation
│   ├── rate_limit.py        # Rate limiting middleware
│   └── logging.py           # Request logging with correlation IDs
├── services/
│   ├── normalization.py     # Request normalization & allowlisting
│   ├── validation.py        # SAR validation service (wraps sar_parser)
│   └── persistence.py       # Repository pattern for database access
└── utils/
    ├── hash.py              # Evidence hash computation
    └── telemetry.py         # Metrics and observability

migrations/                  # Alembic database migrations
docker/                      # Docker configuration
tests/                       # Comprehensive test suite
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=api --cov-report=html

# Run specific test file
pytest tests/test_api/test_sar_submission.py -v
```

Current test coverage: **42 tests, all passing** ✅

## Configuration

Key environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret for JWT token validation
- `JWT_REQUIRED_SCOPE`: Required scope for API access (default: `sar:write`)
- `REDIS_URL`: Redis URL for rate limiting
- `RATE_LIMIT`: Rate limit (default: `100/minute`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

## Security

- **TLS**: All traffic over HTTPS (nginx handles TLS termination)
- **Authentication**: JWT bearer tokens with expiration
- **Authorization**: Scope-based access control (`sar:write` required)
- **Input Validation**: Pydantic models + SAR XML validation
- **Rate Limiting**: Per-IP request throttling
- **Audit Logging**: All requests logged with correlation IDs
- **Content Hashing**: SHA256 hashes for evidence integrity

## Monitoring

### Health Endpoints

- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check (verifies DB and Redis)

### Metrics

- `GET /metrics` - Prometheus metrics endpoint

Key metrics:
- `sar_submissions_total` - Total submission attempts by status
- `sar_submission_duration_seconds` - Submission processing duration
- `validation_errors_total` - Total validation errors
- `database_operation_duration_seconds` - Database operation latency

## Development

### Adding a New Endpoint

1. Create route handler in `api/routes/`
2. Add request/response schemas in `api/models/schemas.py`
3. Include router in `api/main.py`
4. Add tests in `tests/test_api/`

### Running Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

**Issue**: Connection refused to PostgreSQL
- **Solution**: Ensure PostgreSQL is running and `DATABASE_URL` is correct

**Issue**: Rate limiting not working
- **Solution**: Check that Redis is running and `REDIS_URL` is correct

**Issue**: JWT token validation fails
- **Solution**: Verify `JWT_SECRET_KEY` matches between token generation and API

**Issue**: SSL certificate errors
- **Solution**: For local development, use `-k` flag with curl or trust the self-signed cert

## License

This project is part of the stop-azs investigation repository.

## Contributing

See `COPILOT_INSTRUCTIONS.md` for development guidelines.
