# stop-azs

## Features
- Normalizes Azure resource configurations into a consistent structure for auditing.

## SAR Case Packet Workflow
Run all commands from the repository root unless otherwise noted.

### Quick Start
```
cd case_packet
make validate                  # show CSV validator outputs (if any)
make filters-dryrun            # preview Jira API calls (no execution)
cp SAR_Package/jira_filters.env.example SAR_Package/jira_filters.env
$EDITOR SAR_Package/jira_filters.env  # set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY
make filters                   # real creation of saved filters
```

### One-shot
```
cd case_packet
make all   # asks for confirmations at each step
```

### Optional
- Patch the Story Points field ID in the import mapping: `make mapping-patch FIELD=customfield_10016`
- Rebuild the zip archive: `make zip`

### Files
- `SAR_Package/Jira_Saved_Filters.jsonl` – filter definitions for API import
- `SAR_Package/jira_filters_bulk_create.sh` – creates filters and shares them with the project
- `SAR_Package/jira_filters_bulk_create_dryrun.sh` – prints curl commands only
- `SAR_Package/jira_filters.env.example` – environment template (copy to `jira_filters.env`)
- `SAR_Package/Jira_Cloud_Import_Mapping*.json` – CSV import field mappings
- `SAR_Package/JQL_Seeds.md` – JQL blocks used to generate saved filters
