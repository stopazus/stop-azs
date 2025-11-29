# Request Flow: Client Endpoint to Database

This document traces how a client request moves from the public API endpoint to the relational database. It assumes an HTTPS API that accepts Suspicious Activity Report (SAR) XML payloads and relies on the `sar_parser` utilities to validate payloads before persisting records.

## Key Components
- **Client** — Browser, mobile app, or partner integration that posts SAR XML over HTTPS with authentication headers.
- **Edge** — API gateway or load balancer that terminates TLS, throttles abusive traffic, and forwards only well-formed requests.
- **API service** — Parses the request, enforces authentication/authorization, checks body size and content type, delegates schema validation to `sar_parser`, and records metrics/logs for observability.
- **Data access layer (DAL)** — Executes parameterized SQL inside explicit transactions to write normalized SAR records and their related transactions.
- **Database** — Primary relational store (e.g., PostgreSQL) that holds SAR filings and transaction details.

## Sequence Overview

1. **Client submission** — The client sends an HTTPS request (for example, `POST /api/sar`) with auth headers and a SAR XML payload.
2. **Edge protections** — The gateway terminates TLS, applies rate limiting, and forwards only well-formed HTTPS traffic to the app tier.
3. **Ingress filtering** — The API service parses headers and body, enforces authentication/authorization, and performs guardrails such as maximum body size and content type (`application/xml`). Unauthorized or unauthenticated calls exit early with 401/403 responses.
4. **Schema and semantic validation** — The XML body is passed to `sar_parser.validate_string`, which verifies the `<SAR>` root, required sections (filer, subjects, transactions), and disallows placeholder values. Validation errors map to structured 400 responses that echo field-level issues back to the client.
5. **Domain processing** — The backend normalizes validated payloads, derives computed fields (for example, filing metadata), evaluates idempotency keys to avoid duplicates, and prepares database-ready representations.
6. **Persistence** — The DAL runs parameterized SQL in a transaction to insert or upsert SAR records and related transaction rows. Any exception triggers a rollback and produces a sanitized 500 response.
7. **Response** — On success, the API returns a 201 with stored record identifiers and derived metadata. Idempotent replays can return 200 with existing record details. Validation failures return 400 errors, auth issues return 401/403 codes, and database failures return 500 errors.

## Response Map

| Condition                          | Action/Handler                                 | Outcome |
|------------------------------------|-----------------------------------------------|---------|
| Missing/invalid auth               | Edge/API authn/z check                        | `401 Unauthorized` or `403 Forbidden` |
| Unsupported media type or oversized body | Ingress checks on content type/length         | `400 Bad Request` with reason |
| Schema/semantic validation failure | `sar_parser.validate_string`                  | `400 Bad Request` with field errors |
| Idempotent replay detected         | DAL checks idempotency key                    | `200 OK` with existing record metadata |
| Successful insert/update           | Transactional SQL writes                      | `201 Created` with record IDs |
| Database/transaction error         | Transaction rollback and error handling       | `500 Internal Server Error` |

## Mermaid Diagram

```mermaid
graph TD
    subgraph ClientTier
        Client["Client / Integrator\nHTTPS POST /api/sar"]
    end

    subgraph Edge
        Gateway["API Gateway / Load Balancer\nTLS termination + rate limits"]
    end

    subgraph App
        App["API Service\nparse + authn/authz + size checks"]
        Validator["Validate SAR XML\n(sar_parser.validate_string)"]
        DAL["Data Access Layer\nSQL + transactions"]
    end

    subgraph Data
        DB[(Relational Database)]
    end

    Client --> Gateway
    Gateway --> App
    Gateway -->|unauthenticated| Error401["401 Unauthorized\nmissing/invalid auth"]
    Gateway -->|forbidden| Error403["403 Forbidden\nauthz failed"]
    App -->|unsupported media / oversize| Error400Ingress["400 Bad Request\ncontent-type/size"]
    App -->|valid XML body| Validator
    Validator -->|schema errors| Error400["400 Bad Request\nvalidation details"]
    Validator -->|normalize + map fields| DAL
    DAL -->|idempotent replay| ResponseIdem["200 OK\nexisting filing"]
    DAL -->|DB failure| Error500["500 Internal Server Error\nerror payload"]
    DAL --> DB
    DB -->|write success| Response["201 Created\nrecord IDs + metadata"]
```
