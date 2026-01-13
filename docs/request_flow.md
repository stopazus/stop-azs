# Request Flow from Client Endpoint to Database

This document explains how a client request carrying suspicious activity data or supporting attachments travels through the platform until it is persisted in the database and prepared for onward agency delivery (IC3, IRS-CI, and FinCEN).

## End-to-end narrative
1. **Client submission** – A user submits SAR XML or supporting evidence to the public endpoint (e.g., `POST /api/cases/{caseId}/attachments`) over HTTPS. The payload includes authentication headers, case identifiers, and either raw XML or binary evidence.
2. **Ingress & authentication** – The API gateway terminates TLS, enforces auth scopes, and applies request-size limits before forwarding to the application ingress controller.
3. **Request normalisation** – The controller normalises metadata (case IDs, filenames, MIME types) and prepares the body for validation.
4. **Content validation** – SAR XML payloads are parsed and validated with the `sar_parser.validate_string` helper to surface schema and placeholder-field issues before they reach downstream systems. Failures return a 4xx response with precise error locations.
5. **Persistence** – Valid requests create or update case rows, attach file metadata, and write validation results into transactional storage. The database transaction also records audit events for traceability.
6. **Agency handoff queuing** – After the commit succeeds, background jobs enqueue deliveries to IC3, IRS-CI, and FinCEN (`attach-ic3`, `attach-irs-ci`, `attach-fincen`), using the persisted attachment IDs as inputs.
7. **Response** – The API returns a 202/201 with references to the saved attachment, validation status, and any queued agency tasks.

## Mermaid flow diagram
```mermaid
flowchart TD
    C[Client<br/>Portal or partner API] -->|HTTPS POST /api/cases/{caseId}/attachments| G[API Gateway<br/>TLS termination & auth]
    G --> I[Ingress Controller<br/>Request size & MIME guard]
    I --> N[Normaliser<br/>Case/attachment metadata]
    N --> V[SAR Validator<br/>sar_parser.validate_string]
    V -->|Invalid| R[4xx response<br/>Validation errors with locations]
    V -->|Valid| P[Persistence Layer<br/>transactional writes]
    P --> D[(Primary Database<br/>cases, attachments, audit)]
    P --> Q[Queue dispatch<br/>attach-ic3 / attach-irs-ci / attach-fincen]
    Q --> W[Background Workers<br/>agency delivery connectors]
    P --> S[API Response<br/>201/202 + attachment ID]
```

## Validation touchpoint
The SAR validator is the main content gate before persistence. It parses XML payloads, checks for required blocks (filer, subjects, transactions), and rejects placeholder values like `UNKNOWN` in required fields so downstream records always contain meaningful data.
