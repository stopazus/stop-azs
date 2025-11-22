# Resource Update Workflow Example

This document demonstrates the "Get Update + Live" workflow for managing external research resources.

## Scenario: Syncing Updates from Gemini Workbench

### Step 1: Check Current Status

First, check the current status of all external resources:

```bash
python3 tools/resource_updater.py
```

Output:
```
# External Resources Status

**Checked At:** 2025-11-22T14:15:00+00:00

| Resource | Status | Last Updated | URL |
| --- | --- | --- | --- |
| Gemini Workbench | ⚪ Unknown | Never | https://gemini.google.com/app/... |
```

### Step 2: Sync Updates from External Resource

After reviewing and syncing content from the Gemini Workbench into `analysis.md` or other
repository files, mark the resource as updated:

```bash
python3 tools/resource_updater.py \
  --update-resource "Gemini Workbench" \
  --status-file .resource_status.json
```

Output:
```
# External Resources Status

**Checked At:** 2025-11-22T14:20:00+00:00

| Resource | Status | Last Updated | URL |
| --- | --- | --- | --- |
| Gemini Workbench | 🟢 Live | 2025-11-22T14:20:00+00:00 | https://gemini.google.com/app/... |
```

### Step 3: Verify Status Persistence

The status is saved in `.resource_status.json` and will persist across runs:

```bash
python3 tools/resource_updater.py --status-file .resource_status.json
```

The resource will still show as 🟢 Live with the timestamp from when it was last updated.

### Step 4: Generate JSON Status Report

For integration with other tools or automated workflows:

```bash
python3 tools/resource_updater.py \
  --status-file .resource_status.json \
  --output-format json
```

Output:
```json
{
  "resources": [
    {
      "name": "Gemini Workbench",
      "url": "https://gemini.google.com/app/...",
      "custodian": "Case Lead (J. Zeig forensic cell)",
      "notes": "AI-assisted write-ups, scenario drafts, and timeline prototypes that feed into `analysis.md`.",
      "last_updated": "2025-11-22T14:20:00+00:00",
      "status": "live"
    }
  ],
  "checked_at": "2025-11-22T14:25:00+00:00"
}
```

## Integration with Evidence Workflow

The resource updater integrates with the existing evidence workflow:

1. **Sync**: Review external workspace (e.g., Gemini Workbench) for new analysis
2. **Get Update**: Copy relevant findings into repository files
3. **Mark Live**: Update resource status using `resource_updater.py`
4. **Commit**: Commit the updated analysis with appropriate evidence logging
5. **Track**: Monitor resource freshness over time using status indicators

This ensures the team maintains awareness of which external resources are actively synchronized
and which may need attention, supporting the evidence chain of custody requirements for IRS-CI
and FinCEN reviewers.
