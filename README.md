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

## Latest SAR Filing Update
- **Filing Type:** Initial (2025-09-11)
- **Contact:** N & S Holding LLC – AML Surveillance Unit
  - Phone: 786-707-7111
  - Email: office@nsholding.us
- **Filer:** N & S Holding LLC, 2640 Hollywood Blvd, Hollywood, FL 33020, US
- **Subjects:** YBH Holdings LLC; Eisenstein Buyers; Zeig IOTA Escrow
- **Transaction (2023-02-09):** Funds originated from Zeig IOTA Escrow, passed through accounts #2304977980 and #2000043165557, and dispersed to YBH Holdings LLC, Eisenstein Buyers, and layered offshore accounts. UETR and dollar amounts pending subpoena from Banesco USA.
- **Suspicious Activity:** Wire fraud (escrow diversion), money laundering (layering), structuring. Narrative references IC3 Submission ID 7065f60922b948a59af3a8654edb16dd.
- **Attachment:** Consolidated_SAR_Report_IC3_7065f60922b948a59af3a8654edb16dd.pdf (annex with transaction tables, flowchart, compliance recommendations, and embedded subpoena request)
