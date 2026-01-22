# Request Flow: Client Endpoint to Database

This document outlines how a SAR validation API would process inbound requests end-to-end, using the existing `sar_parser.validator` utilities for XML inspection before persisting results.

## Narrative Flow
1. **Client submission** – An external client POSTs a SAR XML payload to the validation endpoint (e.g., `/sar/validate`).
2. **Request handling** – The HTTP handler reads the raw XML text from the body and passes it to `validate_string` for validation.
3. **Namespace normalization** – `validate_string` calls `_strip_namespaces` to remove default or prefixed XML namespaces so element lookups are deterministic.
4. **Structural checks** – `_validate_required_blocks` ensures required top-level sections (such as `<FilerInformation>`, `<Subject>`, and `<Transaction>`) exist before deeper inspection.
5. **Transaction checks** – `_validate_transactions` walks each `<Transaction>` to verify amounts are present, not placeholders, and carry a valid three-letter currency code (using the default allowlist plus any custom additions supplied by the endpoint).
6. **Result construction** – The accumulated `ValidationResult` is returned to the handler. If `is_valid` is `True`, the payload is considered ready for persistence.
7. **Database persistence** – Valid documents are written to the storage layer (e.g., a relational database) alongside audit metadata (request ID, timestamps, client identifier). Invalid documents skip persistence but still return structured errors to the caller.

## Mermaid Sequence Diagram
```mermaid
sequenceDiagram
    participant C as Client
    participant API as HTTP Endpoint (/sar/validate)
    participant V as Validator (sar_parser.validator)
    participant DB as Database

    C->>API: POST SAR XML payload
    API->>V: validate_string(xml_text, allowed_currencies)
    V->>V: _strip_namespaces(root)
    V->>V: _validate_required_blocks(root, result)
    V->>V: _validate_transactions(root, result, allowed_currencies)

    alt Validation passes
        V-->>API: ValidationResult (is_valid=True)
        API->>DB: Persist SAR + audit metadata
        DB-->>API: Ack
        API-->>C: 200 OK + receipt
    else Validation fails
        V-->>API: ValidationResult (errors)
        API-->>C: 422 Unprocessable Entity + error list
    end
```

## Integration Notes
- The database layer is intentionally decoupled from the validator; call sites should persist only after receiving a clean `ValidationResult`.
- Custom currency allowlists can be passed through the endpoint to support edge cases without relaxing the core validation behavior.
- Any upstream middleware (rate limiting, auth) should wrap the endpoint before the validation call, since the validator assumes already-trusted input streams.
