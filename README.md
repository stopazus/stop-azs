# stop-azs
This repository documents key allegations and participants in the alleged diversion of escrow funds
from the City National Bank trust account controlled by Justin E. Zeig. See [analysis.md](analysis.md)
for detailed background on the trust account activity, summaries of the shell entities involved,
captured case metadata, identified red flags, an expanded forensic ledger exhibit (as of 24 August
2025), and a concluding synthesis that ties the observed pass-through behavior to the ongoing
recovery and enforcement efforts.

## Master Exhibit Index

A structured registry of all legal exhibits filed with law enforcement agencies (FBI IC3, FinCEN, IRS-CI)
is maintained in [master_exhibit_index.json](master_exhibit_index.json). The index provides Bates numbering,
filing status, cryptographic hashes, and metadata for each exhibit. See 
[docs/master_exhibit_index.md](docs/master_exhibit_index.md) for documentation and usage examples.

## Windows NAS Bootstrap

The [windows-nas-bootstrap](windows-nas-bootstrap/) directory contains a Windows automation bundle that:
- Installs essential applications via winget (Python 3.12, Git, rclone, VS Code, 7-Zip, VLC, WinSCP, PuTTY)
- G:\My Drive\AICD
- Performs optional network speed tests

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

## Testing

The project includes automated tests for key components:
* `tests/test_validator.py` - SAR XML validation tests
* `tests/test_exhibit_index.py` - Master Exhibit Index data structure tests

Run tests with: `python3 tests/test_validator.py` or `python3 tests/test_exhibit_index.py`
