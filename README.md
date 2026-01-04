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

## External Research Resources

Investigators occasionally stage AI-assisted narratives or drafting notes outside the repository before
promoting them into `analysis.md`. A living index of those destinations now lives in
[`docs/external_resources.md`](docs/external_resources.md). Each entry records the location, primary
custodian, and handling expectations so contributors know how to access the Gemini workspace and any future
off-repo staging areas without breaking the evidence trail.

## Testing

The project currently has no automated test suite. A `pytest` run (August 2025) reports zero
collected tests, confirming that no executable checks are defined yet.

## Task Manager Utility

The repository includes a lightweight PowerShell helper, `task_manager.ps1`, for tracking work
items in `tasks.json`. It supports add, update, remove, and list actions so contributors on
Windows can quickly log and adjust tasks.

Example: mark the "Database Migration" task as active with a priority of 2 and two tags.

```powershell
./task_manager.ps1 -Action update -Title "Database Migration" -Status active -Priority 2 -Tags "urgent,database"
```
