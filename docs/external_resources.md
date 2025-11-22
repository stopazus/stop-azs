# External Research Resources

The investigative team often supplements the forensic ledger review with
open-source intelligence tools. This catalog records every off-repository
workspace that contains notes, drafts, or AI-generated material tied to
the escrow diversion matter.

| Resource | URL | Custodian | Notes |
| --- | --- | --- | --- |
| Gemini Workbench | https://gemini.google.com/app/8f7e04aa81aa552a?utm_source=app_launcher&utm_medium=owned&utm_campaign=base_all | Case Lead (J. Zeig forensic cell) | AI-assisted write-ups, scenario drafts, and timeline prototypes that feed into `analysis.md`. |

## Live Status Tracking

To track and monitor the status of external resources, use the `resource_updater.py` tool:

```bash
# View current status of all resources
python3 tools/resource_updater.py

# Mark a resource as recently updated after syncing
python3 tools/resource_updater.py --update-resource "Gemini Workbench" --status-file .resource_status.json

# Check status in JSON format
python3 tools/resource_updater.py --status-file .resource_status.json --output-format json
```

This helps the team maintain awareness of which external workspaces have been recently
synchronized and which may require attention.

## Operational Guidance

- **Access coordination:** Request access through the listed custodian so
  sharing remains scoped to investigators already cleared on the escrow
  matter.
- **Synchronization discipline:** Before running a new prompt, copy the
  latest City National Bank ledger excerpts or supporting documents into
  the workspace so Gemini outputs reflect current evidence.
- **Evidence logging:** Capture prompt/response hashes and timestamps in
  the weekly evidence log to preserve traceability for IRS-CI and
  FinCEN reviewers.
- **Repository promotion:** Export any final text snippets into this
  repository (for example, `docs/` or `analysis.md`) so the auditable
  chain of custody remains intact.
- **Adding new resources:** When introducing another external tool,
  extend the table above with its URL, custodian, and usage rationale so
  subsequent reviewers know why the workspace exists and how to treat
  its contents.
