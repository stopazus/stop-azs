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

See [windows-nas-bootstrap/README.md](windows-nas-bootstrap/README.md) for usage instructions.

## SAR Parser Utilities

The `sar_parser` package contains helper utilities that can be reused in
automation workflows:

- `validate_string` and `validate_file` perform structural checks on SAR
  XML documents and collect actionable validation errors.
- `sar_parser.live_update` offers a "live update" mode that continuously
  monitors a SAR file on disk and re-runs the validator whenever the file
  changes. You can launch it via `python -m sar_parser.live_update path/to/file.xml`.

## Testing

Run the Python unit tests to verify the validator and live update helper:

```bash
python -m pytest
```
