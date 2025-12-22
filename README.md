# stop-azs
This repository documents key allegations and participants in the alleged diversion of escrow funds
from the City National Bank trust account controlled by Justin E. Zeig. See [analysis.md](analysis.md)
for detailed background on the trust account activity, summaries of the shell entities involved,
captured case metadata, identified red flags, an expanded forensic ledger exhibit (as of 24 August
2025), and a concluding synthesis that ties the observed pass-through behavior to the ongoing
recovery and enforcement efforts.

## Windows NAS Bootstrap

The [windows-nas-bootstrap](windows-nas-bootstrap/) directory contains a Windows automation bundle that:
- Installs essential applications via winget (Python 3.12, Git, rclone, VS Code, 7-Zip, VLC, WinSCP, PuTTY)
- Maps Google Drives (https://drive.google.com/drive/folders/1UwPxnoQJcSaeBRCkIkZ2aV2_lGcVlhcB?usp=sharing)
- Reconnects NAS-hosted cloud mirrors to standard drive letters (G:, I:, O:) documented in
  [docs/nas_drive_mapping.md](docs/nas_drive_mapping.md) so investigators can restore shortcuts after
  reinstalls.

See [windows-nas-bootstrap/README.md](windows-nas-bootstrap/README.md) for usage instructions and
the drive-mapping reference.

## External Research Resources

Investigators occasionally stage AI-assisted narratives or drafting notes outside the repository before
promoting them into `analysis.md`. A living index of those destinations now lives in
[`docs/external_resources.md`](docs/external_resources.md). Each entry records the location, primary
custodian, and handling expectations so contributors know how to access the Gemini workspace and any future
off-repo staging areas without breaking the evidence trail.

## SAR Validation Request Flow

SAR validation requests originate at a public API endpoint and traverse the gateway, controller, validator,
and database. The sequence below mirrors the `sar_parser.validator` usage and persistence expectations
captured in [`docs/request_flow.md`](docs/request_flow.md):

1. **Client submission** – Caller POSTs SAR XML and metadata (submitter ID, source system) to
   `POST /api/sar/validate` or an equivalent ingress endpoint.
2. **Gateway routing** – The gateway authenticates/authorizes the caller, attaches a correlation ID,
   and forwards the payload to the validation service.
3. **Controller handling** – The controller reads the XML body (or streams from object storage) and invokes
   `sar_parser.validator.validate_string` or `validate_file` for in-memory validation.
4. **Validator execution** – The validator parses required SAR sections, rejects placeholder values, and
   returns a `ValidationResult` with any `ValidationError` entries.
5. **Database transaction** – The controller opens a transaction and persists request metadata, validation
   summary, and individual errors in a deterministic order before committing.
6. **Response assembly** – The service returns JSON containing the correlation ID, `is_valid` flag, and
   any validation errors so the client can remediate or proceed to filing.

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

## Testing

The project currently has no automated test suite. A `pytest` run (August 2025) reports zero
collected tests, confirming that no executable checks are defined yet.
