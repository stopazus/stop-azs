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
- Maps NAS cloud storage drives (G:, I:, O:)
- Performs optional network speed tests
- Targets the AICD Google Drive sync root at `Z:\My Drive\AICD`

See [windows-nas-bootstrap/README.md](windows-nas-bootstrap/README.md) for usage instructions.

## External Research Resources

Investigators occasionally stage AI-assisted narratives or drafting notes outside the repository before
promoting them into `analysis.md`. A living index of those destinations now lives in
[`docs/external_resources.md`](docs/external_resources.md). Each entry records the location, primary
custodian, and handling expectations so contributors know how to access the Gemini workspace and any future
off-repo staging areas without breaking the evidence trail.

## Request Flow

The end-to-end path for a client submission—from the public API endpoint through validation and into the
database—is captured in [`docs/request_flow.md`](docs/request_flow.md), including a Mermaid diagram that
highlights each security, validation, and persistence hop.

## Manifest Signing Environment Variables

Some workflows require manifest signing credentials to be available as environment variables. Use
a secure secret store to retrieve values at runtime, and avoid committing real secrets into shell
history or files tracked by Git.

**Windows PowerShell**
```powershell
$env:MANIFEST_KEY_ID="YOUR_KEY_ID"
$env:MANIFEST_HMAC_KEY="YOUR_LONG_SECRET_OR_BASE64"
```

**macOS/Linux (bash/zsh)**
```bash
export MANIFEST_KEY_ID="YOUR_KEY_ID"
export MANIFEST_HMAC_KEY="YOUR_LONG_SECRET_OR_BASE64"
```

## Testing

The project currently has no automated test suite. A `pytest` run (August 2025) reports zero
collected tests, confirming that no executable checks are defined yet.
