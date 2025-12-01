# Request Flow: Client Endpoint to Database

This guide traces how a Suspicious Activity Report (SAR) submission moves through the service—from the client call into the HTTP endpoint through validation and finally into durable storage. The Mermaid diagram highlights both the happy-path validation and the audit trail recorded for failed requests.

## End-to-end sequence

1. **Client request** – A user interface or integration partner issues an HTTPS `POST` to `/api/sar/validate` with an XML payload and authentication headers.
2. **Edge handling** – The API gateway or load balancer terminates TLS, enforces rate limits, and drops unauthenticated or abusive traffic before it reaches the app tier.
3. **Routing & coarse checks** – The application controller verifies content type, body size, and required headers, returning a 4xx immediately if the request is malformed.
4. **Normalization** – The request validator trims whitespace, enforces a consistent encoding, and prepares the XML body for schema-aware inspection.
5. **Domain validation** – The SAR-specific validator (the `validate_string` path in [`sar_parser/validator.py`](../sar_parser/validator.py)) enforces structural requirements (SAR root, filer block, subjects, and transactions) and semantic rules (for example, rejecting placeholder or zero-amount transactions).
6. **Result aggregation** – Findings are normalized into a response envelope containing `is_valid` and a list of errors. Both success and failure outcomes are captured for persistence.
7. **Persistence** – Submission metadata, timing data, `is_valid`, and normalized errors are written to the operational database so auditors can reconstruct what was received and why it passed or failed.
8. **Client response** – The API returns HTTP 200 with the validation result while the stored record preserves the request context and findings.

## Mermaid diagram

```mermaid
flowchart TD
    A[Client (UI / Partner Integration)] -->|HTTPS POST /api/sar/validate| B[API Gateway / Load Balancer]
    B -->|TLS termination & auth| C[Application Endpoint]
    C -->|Content type + size checks| D[Request Validator]
    D -->|Normalize XML| E[Domain Validation (validate_string)]
    E -->|Outcome + errors| F[Response Builder]
    E -->|Record metadata + errors| G[Persistence Layer]
    G -->|Insert audit row| H[(Operational Database)]
    F -->|HTTP 200 with is_valid + errors| A
```

## Component responsibilities

- **API gateway / load balancer**: Terminates TLS, enforces authentication and rate limiting, and shields the application tier from malformed or abusive traffic.
- **Application endpoint**: Routes requests, performs coarse validation (content type, body size), and maps client identity for logging and rate decisions.
- **Request validator**: Normalizes the XML body, rejects empty submissions early, and prepares the content for schema-aware inspection.
- **Domain validation**: Implements SAR-specific checks such as ensuring a `<SAR>` root, required blocks (`<FilerInformation>`, `<Subjects>`, `<Transactions>`), and non-placeholder amounts inside each transaction, mirroring the logic in `sar_parser/validator.py`.
- **Response builder**: Returns a concise payload containing `is_valid` and any validation errors so clients can remediate issues without re-sending the SAR.
- **Persistence layer**: Writes submission metadata and validation results to the database to support audit trails, analytics, and downstream case management.

## Request and response shape

- **Input contract**: `POST /api/sar/validate` expects an XML body and authentication headers. The payload is normalized before validation to avoid schema drift.
- **Validation algorithm**: The parser follows the `validate_string` pathway in [`sar_parser/validator.py`](../sar_parser/validator.py), which enforces SAR root presence and structural requirements for filer, subject, and transaction blocks before performing semantic checks (e.g., rejecting placeholder dollar amounts).
- **Response contract**: The service returns an HTTP `200` with `{ "is_valid": <bool>, "errors": [<message>...] }`. Errors are aggregated from the domain validator and mirrored in the stored record for traceability.

## Persistence details

| Field / area        | Purpose                                                        | Source                                        |
| ------------------- | -------------------------------------------------------------- | --------------------------------------------- |
| `request_id`        | Correlates incoming request to stored audit row                | Gateway / controller generated identifier      |
| `submitter`         | Records the authenticated caller for traceability             | Authentication context                        |
| `received_at`       | Timestamps the ingress time                                    | Controller clock                              |
| `validated_at`      | Captures when validation completed                             | Validator timing                              |
| `is_valid`          | Boolean result of `validate_string`                            | Domain validation                             |
| `errors`            | Normalized error list returned to the client and stored as-is  | Domain validation aggregation                 |
| `normalized_payload`| Cleaned XML copy used by the validator (optional for replay)   | Request validator output                      |

- **Auditability**: Storing both the normalized errors and request metadata ensures reviewers can reproduce the validation outcome long after the client has received the response, including which input was evaluated and when.
