# SAR Submission API Usage Guide

## Authentication

The API uses JWT bearer tokens with scope validation. To access the API, you need a valid JWT token with the `sar:write` scope.

### Obtaining a JWT Token (Development)

For development and testing, you can generate JWT tokens using Python:

```python
import jwt
from datetime import datetime, timedelta

# Token payload
payload = {
    "sub": "test-user@example.com",  # Subject (user identity)
    "scope": "sar:write",             # Required scope
    "exp": datetime.utcnow() + timedelta(hours=1),  # Expiration
    "iat": datetime.utcnow()          # Issued at
}

# Generate token
token = jwt.encode(
    payload,
    "dev_secret_change_in_production",  # Match JWT_SECRET_KEY in .env
    algorithm="HS256"
)

print(f"Bearer {token}")
```

Or use the provided helper script:

```bash
python tools/generate_jwt.py --subject "user@example.com" --scope "sar:write" --hours 1
```

## API Endpoints

### Submit SAR Record

**Endpoint:** `POST /api/sar-records`

**Headers:**
- `Authorization: Bearer <jwt-token>`
- `Content-Type: application/json`
- `X-Request-ID: <optional-correlation-id>` (auto-generated if not provided)

**Request Body:**

```json
{
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
  ],
  "idempotency_key": "unique-key-12345"
}
```

**Success Response (201 Created):**

```json
{
  "record_id": "550e8400-e29b-41d4-a716-446655440000",
  "request_id": "req_abc123xyz",
  "submitted_at": "2024-05-01T12:34:56.789Z"
}
```

**Validation Error Response (422 Unprocessable Entity):**

```json
{
  "detail": "Validation failed",
  "errors": [
    {
      "message": "At least one <Subject> is required.",
      "location": "/SAR/Subjects",
      "severity": "error"
    }
  ],
  "request_id": "req_abc123xyz"
}
```

### Health Check

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-05-01T12:34:56.789Z",
  "version": "1.0.0"
}
```

### Readiness Check

**Endpoint:** `GET /health/ready`

**Response:**

```json
{
  "status": "ready",
  "timestamp": "2024-05-01T12:34:56.789Z",
  "database": "connected",
  "redis": "connected"
}
```

### Metrics

**Endpoint:** `GET /metrics`

Returns Prometheus-format metrics for monitoring.

## Example API Calls

### Using curl

```bash
# Generate a JWT token first
export JWT_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Submit a SAR record
curl -X POST https://localhost/api/sar-records \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filing_type": "Initial",
    "filing_date": "2024-05-01",
    "filer_name": "Example Financial",
    "filer_address": {
      "address_line1": "123 Main St",
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
  }'

# Check health
curl https://localhost/health/ready
```

### Using Python (httpx)

```python
import httpx
import jwt
from datetime import datetime, timedelta

# Generate token
payload = {
    "sub": "api-user@example.com",
    "scope": "sar:write",
    "exp": datetime.utcnow() + timedelta(hours=1),
    "iat": datetime.utcnow()
}
token = jwt.encode(payload, "dev_secret_change_in_production", algorithm="HS256")

# Make request
with httpx.Client(verify=False) as client:  # verify=False for self-signed cert
    response = client.post(
        "https://localhost/api/sar-records",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "filing_type": "Initial",
            "filing_date": "2024-05-01",
            "filer_name": "Example Financial",
            "filer_address": {
                "address_line1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "US"
            },
            "subjects": [{"name": "John Doe", "entity_type": "Individual"}],
            "transactions": [{"date": "2024-04-30", "amount": "1000.50", "currency": "USD"}]
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
```

## Idempotency

To prevent duplicate submissions, include an `idempotency_key` in your request. If the same key is used in multiple requests, only the first submission will be processed, and subsequent requests will return the original record.

```json
{
  "idempotency_key": "my-unique-transaction-id-12345",
  ...
}
```

## Error Handling

### Common Error Codes

- **400 Bad Request:** Malformed JSON or invalid field types
- **401 Unauthorized:** Missing, expired, or invalid JWT token
- **403 Forbidden:** Token lacks required `sar:write` scope
- **422 Unprocessable Entity:** Validation failed (see errors array)
- **429 Too Many Requests:** Rate limit exceeded (includes Retry-After header)
- **503 Service Unavailable:** Database or service error

### Best Practices

1. **Always include an idempotency key** for production submissions
2. **Handle 429 rate limit errors** by respecting the Retry-After header
3. **Log the request_id** from responses for troubleshooting
4. **Validate data client-side** before submission to catch errors early
5. **Use exponential backoff** for retrying failed requests

## Rate Limiting

Default rate limits:
- 100 requests per minute per IP address
- Burst capacity of 20 additional requests

When rate limited, the API returns:
- Status code: 429
- Retry-After header indicating when to retry

## Security Notes

- **Never log JWT tokens** in client applications
- **Rotate JWT secrets regularly** in production
- **Use HTTPS only** - the API redirects HTTP to HTTPS
- **Validate SAR data** before submission to avoid leaking sensitive information in validation errors
- **Store idempotency keys securely** to prevent replay attacks

## Production Deployment

For production use:

1. **Replace JWT secret:** Set a strong, random `JWT_SECRET_KEY`
2. **Use managed PostgreSQL:** Configure `DATABASE_URL` to production database
3. **Configure IP allowlist:** Set `ALLOWED_IPS` if needed
4. **Enable HTTPS:** Use valid SSL certificates (not self-signed)
5. **Monitor metrics:** Set up Prometheus/Grafana for `/metrics` endpoint
6. **Configure logging:** Send structured logs to centralized logging system
7. **Set up backups:** Regular database backups and disaster recovery plan
