# Request Flow: Client Endpoint to Database

This document explains the end-to-end path for a client submission entering the Suspicious Activity Report (SAR) intake endpoint and being persisted in the investigation datastore. It pairs narrative detail with a Mermaid diagram for quick reference.

## High-Level Steps

1. **Client submits SAR payload** via `POST /api/sar/validate` over HTTPS, providing the XML document and authentication token.
2. **API gateway / edge** terminates TLS, enforces request limits, and forwards authenticated calls to the application service.
3. **Request handler** (e.g., a FastAPI/Flask controller) unmarshals the request body, extracts the XML string, and resolves user context.
4. **SAR validator service** invokes `sar_parser.validate_string` to inspect structure and semantic requirements (required blocks, placeholder detection, etc.).
5. **Validation decision**:
   - If errors exist, the handler returns a 400 response detailing the `ValidationError` entries and does not persist the document.
   - If valid, the handler proceeds to persistence.
6. **Persistence layer** writes the normalized record to the relational database (e.g., PostgreSQL) inside a transaction:
   - Store core filing metadata and submitter context in the `filings` table.
   - Store each validation run and outcome in a `validation_events` table for auditability.
   - Persist the raw XML in a `documents` table or object storage reference for later review.
7. **Response to client** confirms success (HTTP 201) and returns identifiers for the filing and validation event.

## Detailed Interaction Notes

- **Authentication & Authorization**: The edge layer verifies tokens and enforces role-based access. Downstream services trust the propagated identity (e.g., via JWT claims) to scope database writes.
- **Idempotency**: The handler calculates a content hash of the XML; repeat submissions with the same hash return the existing filing ID instead of duplicating rows.
- **Observability**: Structured logs capture each step with correlation IDs. Validation failures are emitted as warning-level events; successful persists emit audit logs linking the filing ID and user identity.
- **Error Handling**: Malformed XML triggers an early 400 response from the validator. Database errors surface as 500 responses with generic messaging while preserving detailed traces in logs/metrics.

## Mermaid Diagram

```mermaid
flowchart LR
    Client[Client or Partner System\nPOST /api/sar/validate]
    Edge[API Gateway / TLS Termination]
    Handler[Request Handler\n(FastAPI/Flask)]
    Validator[Validator Service\n sar_parser.validate_string]
    DB[(PostgreSQL)]
    Documents[documents]
    Filings[filings]
    Events[validation_events]

    Client --> Edge --> Handler --> Validator
    Validator -- ValidationResult --> Handler
    Handler -- valid --> DB
    DB -.->|store raw XML| Documents
    DB -.->|store filing metadata| Filings
    DB -.->|store validation events| Events
    Handler -. invalid .-> Client
    Handler -->|201 + IDs| Client
```

The diagram follows the same logical flow as the narrative: the client request is authenticated at the edge, parsed and validated by the handler using the existing `sar_parser` module, and stored in PostgreSQL with audit trails before responding.
