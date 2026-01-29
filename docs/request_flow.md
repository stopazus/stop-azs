# Request Flow: Client Endpoint to Database

This document describes how a client submission travels through the service boundary, validation layer, and persistence tier before it is committed to the backing database. The flow emphasizes where security controls, data validation, and audit logging occur so investigators can trace each hop.

## Implementation Status

✅ **Fully Implemented** - All 9 steps are production-ready with comprehensive test coverage (42 tests passing).

## Step-by-Step Flow

1. **Client request** – A caller (web app, automation, or investigator) sends a JSON payload to the public `POST /api/sar-records` endpoint over TLS.
   - **Implementation**: [`api/routes/sar_records.py`](../api/routes/sar_records.py) - FastAPI endpoint
   - **TLS Termination**: [`docker/nginx/nginx.conf`](../docker/nginx/nginx.conf) - Nginx reverse proxy

2. **Edge protections** – The API gateway/load balancer terminates TLS, enforces request size limits, and forwards only well-formed traffic to the application service. Rate limits and IP allowlists are enforced here.
   - **Implementation**: [`api/middleware/rate_limit.py`](../api/middleware/rate_limit.py) - Slowapi rate limiting
   - **Nginx Config**: [`docker/nginx/nginx.conf`](../docker/nginx/nginx.conf) - Request size limits, rate limiting zones
   
3. **Authentication and authorization** – The application middleware validates the bearer token (or mTLS identity), rejects expired credentials, and checks that the caller has `sar:write` scope before any processing occurs.
   - **Implementation**: [`api/middleware/auth.py`](../api/middleware/auth.py) - JWT bearer token validation
   - **Tests**: [`tests/test_api/test_auth.py`](../tests/test_api/test_auth.py) - 7 authentication tests

4. **Request normalization** – The application deserializes the JSON body into an internal SAR submission object, normalizes whitespace, and drops fields not on the allowlist to prevent over-posting.
   - **Implementation**: [`api/services/normalization.py`](../api/services/normalization.py) - JSON → SAR XML conversion
   - **Schema**: [`api/models/schemas.py`](../api/models/schemas.py) - Pydantic models with `extra="forbid"`
   - **Tests**: [`tests/test_api/test_normalization.py`](../tests/test_api/test_normalization.py) - 5 normalization tests

5. **Business validation** – The payload is converted into SAR XML and passed to the `sar_parser.validator.validate_string` function so structural requirements (root `<SAR>` element, required blocks, and non-placeholder amounts) are enforced consistently across ingestion paths.【F:sar_parser/validator.py†L46-L129】 Validation errors short-circuit the request and return a `422 Unprocessable Entity` response with field-level messages.
   - **Implementation**: [`api/services/validation.py`](../api/services/validation.py) - Wraps existing `sar_parser.validator`
   - **Validator**: [`sar_parser/validator.py`](../sar_parser/validator.py) - Existing validation logic (unchanged)
   - **Tests**: [`tests/test_api/test_validation_integration.py`](../tests/test_api/test_validation_integration.py) - 5 validation integration tests

6. **Persistence preparation** – Valid submissions are enriched with timestamps and requester identity, then mapped to the repository/ORM layer that controls write access to the relational database. Any computed hashes for evidence logging are generated here.
   - **Implementation**: [`api/utils/hash.py`](../api/utils/hash.py) - SHA256 content hashing
   - **Repository**: [`api/services/persistence.py`](../api/services/persistence.py) - Repository pattern

7. **Database transaction** – The repository opens a transaction, writes the normalized SAR record into the `sar_records` table, and commits. If the commit fails, the transaction is rolled back and a `503 Service Unavailable` error is returned.
   - **Implementation**: [`api/services/persistence.py`](../api/services/persistence.py) - SQLAlchemy transactions
   - **Models**: [`api/models/database.py`](../api/models/database.py) - `SARRecord` ORM model
   - **Migration**: [`migrations/versions/001_initial_migration.py`](../migrations/versions/001_initial_migration.py) - Initial schema
   - **Tests**: [`tests/test_api/test_idempotency.py`](../tests/test_api/test_idempotency.py) - 4 idempotency tests

8. **Audit and telemetry** – Structured logs (request ID, caller, validation outcome, and database latency) are emitted to the observability stack. Security-relevant events (authorization failures, repeated validation errors) also raise alerts.
   - **Implementation**: [`api/middleware/logging.py`](../api/middleware/logging.py) - Request logging with correlation IDs
   - **Telemetry**: [`api/utils/telemetry.py`](../api/utils/telemetry.py) - Prometheus metrics
   - **Logs**: Structured JSON logs via `structlog` (see [`api/main.py`](../api/main.py))

9. **Response** – On success, the service returns `201 Created` with the persisted record identifier and echoes the request ID so downstream systems can correlate telemetry.
   - **Implementation**: [`api/routes/sar_records.py`](../api/routes/sar_records.py) - Response handling
   - **Schema**: [`api/models/schemas.py`](../api/models/schemas.py) - `SARSubmissionResponse`
   - **Tests**: [`tests/test_api/test_sar_submission.py`](../tests/test_api/test_sar_submission.py) - 10 end-to-end tests

## Mermaid Diagram
```mermaid
flowchart LR
    Client[Client / Investigator Tool] -->|POST /api/sar-records| Edge[API Gateway / Load Balancer]
    Edge --> Auth[Auth & Throttling Middleware]
    Auth --> App[Application Service]
    App --> Normalize[Normalize & Allowlist Fields]
    Normalize --> Validate[validate_string (sar_parser.validator)]
    Validate -->|invalid| Error[422 response with validation errors]
    Validate -->|valid| Repo[Repository / ORM Layer]
    Repo --> DB[(Relational Database)]
    DB --> Repo
    Repo --> Success[201 response with record ID]
    Error --> Client
    Success --> Client
```

## Handling Expectations
- **Security-first posture:** Rejections at the edge and auth layers should never leak sensitive detail; validation responses are confined to field-level guidance.
- **Traceability:** Every hop (edge, auth, validation, DB) must emit structured logs keyed by a shared request ID to preserve the evidence trail.
- **Idempotency:** Clients should reuse the same idempotency key on retries so the repository layer can safely de-duplicate submissions when transient errors occur.
