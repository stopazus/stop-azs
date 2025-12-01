# SAR Validation Request Flow

This document summarizes how a Suspicious Activity Report (SAR) validation request moves from the public API endpoint through validation and into durable storage using the `sar_parser.validator` module.

## End-to-End Flow

1. **Client submission** – A client POSTs a SAR XML payload and contextual metadata (submitter ID, source system) to the public endpoint (e.g., `POST /api/sar/validate`).
2. **API gateway & routing** – The ingress layer authenticates/authorizes the caller, attaches a correlation ID, and forwards the request to the validation service.
3. **Validation controller** – The controller reads the request body and calls `sar_parser.validator.validate_string` for in-memory XML validation. If the payload is streamed from object storage, the controller uses `validate_file` with the fetched object handle.
4. **Validator execution** – The validator parses the XML, verifies required elements (such as `<FilerInformation>`, `<Subject>`, and `<Transaction>`), rejects placeholder values, and assembles a `ValidationResult` with any `ValidationError` entries.
5. **Database transaction** – The controller opens a database transaction and writes the artifacts in a deterministic order:
   - **requests**: correlation ID, submitter, source system, received timestamp, and a pointer to the raw payload if it is stored externally.
   - **validation_results**: foreign key to `requests`, `is_valid` flag, error count, and creation timestamp.
   - **validation_errors**: foreign key to `validation_results`, error message, location, and severity.
   The transaction commits only after all tables are populated so the database reflects a consistent request-to-errors lineage.
6. **Response assembly** – The service returns a JSON body containing the correlation ID, the `is_valid` flag, and any validation errors so the client can fix issues or proceed to downstream filing. Primary keys from the inserted rows can be echoed for audit or reprocessing.

## Mermaid Diagram

```mermaid
flowchart TD
    Client[Client \n e.g., filing portal or automation job]
    APIGW[API Gateway / Ingress]
    Controller[Validation Controller]
    Validator[Python validator\n sar_parser.validator]
    DB[(Relational DB \n requests, validation_results, validation_errors)]
    Storage[Object Storage \n optional XML retention]

    Client -->|POST /api/sar/validate\nSAR XML + metadata| APIGW
    APIGW -->|AuthN/AuthZ\nAdd correlation ID| Controller
    Controller -->|Read body / stream| Validator
    Validator -->|ValidationResult\nerrors & flags| Controller
    Controller -->|Persist metadata & results| DB
    Controller -->|Store raw XML (optional)| Storage
    Controller -->|JSON response\ncorrelation ID + errors| Client
```

## Operational Notes

- The validator runs in memory and has no external dependencies, so it can execute in stateless application pods or serverless functions.
- Persisting the raw XML payload in object storage keeps the database lean while retaining auditable inputs for reprocessing.
- Correlation IDs should propagate through logs and responses to simplify tracing across the gateway, controller, validator, and database tiers.
