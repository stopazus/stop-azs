# Request Flow: Client Endpoint to Database

This document describes how a client request is processed from the public endpoint through validation and persistence. The flow is framed around the SAR validation utilities contained in `sar_parser`, showing where the validator participates before data is stored.

## Textual Overview
1. **Client submits data** to the public API endpoint (e.g., `POST /api/sar`).
2. **API Gateway / Load Balancer** authenticates the caller, enforces TLS, and forwards the request to the application service.
3. **Application Service** parses the payload and routes SAR submissions to the validation stage.
4. **Validation Layer (`sar_parser.validator`)** runs structural and semantic checks, returning a `ValidationResult` with actionable errors if issues are found.
5. **Business Logic** transforms validated SAR data into persistence models and enriches metadata (timestamps, request IDs, user context).
6. **Database Layer** executes parameterized inserts/updates within a transaction and emits audit logs for downstream monitoring.

## Mermaid Sequence Diagram
```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant G as API Gateway / LB
    participant S as App Service
    participant V as Validator (sar_parser)
    participant B as Business Logic
    participant D as Database

    C->>G: HTTPS POST /api/sar (XML payload)
    G->>G: AuthN/Z, rate limits, request logging
    G->>S: Forward validated request context
    S->>V: validate_string(xml_payload)
    V-->>S: ValidationResult (errors | ok)
    alt Validation errors
        S-->>C: 400 Bad Request + error list
    else Valid submission
        S->>B: Build persistence model, add metadata
        B->>D: Parameterized INSERT/UPDATE within transaction
        D-->>B: Commit success (row IDs, timestamps)
        B-->>C: 202 Accepted (tracking reference)
    end
```

## Operational Notes
- **Authentication and rate limiting** should live in the gateway to protect the application from abusive traffic.
- **Validation failures** should return descriptive messages sourced from `ValidationResult.errors` to help clients correct submissions.
- **Database interactions** must use prepared statements and transactions to prevent injection and ensure atomic writes.
- **Audit logging** is recommended at the gateway, application, and database layers to support forensic review.
