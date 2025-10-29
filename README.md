# stop-azs

## Features
- Normalizes Azure resource configurations into a consistent structure for auditing.

## Testing
- Install project dependencies if necessary, then run `pytest` from the repository root to execute the automated test suite.

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
- **Contacts (each has confirmed receipt of the full SAR packet):**
  - N & S Holding LLC – AML Surveillance Unit (Phone: 786-707-7111, Email: office@nsholding.us). **Status:** Confirmed full SAR update delivered via secure email on 2025-09-11.
  - FBI – Internet Crime Complaint Center (IC3), Recovery Asset Team (RAT), Reference: IC3 Submission ID 7065f60922b948a59af3a8654edb16dd. **Status:** Confirmed packet received and acknowledged by RAT liaison on 2025-09-11.
  - FinCEN – BSA E-Filing, Suspicious Activity Report (SAR) Program. **Status:** Automatic confirmation of submission and packet dissemination logged 2025-09-11 14:37 ET.
  - IRS – Criminal Investigation (IRS-CI), Fraud / Money Laundering Referral Program. **Status:** Case agent acknowledgment received 2025-09-11 with reference CI-2025-341.
- **Filer:** N & S Holding LLC, 2640 Hollywood Blvd, Hollywood, FL 33020, US
- **Subjects:** YBH Holdings LLC; Eisenstein Buyers; Zeig IOTA Escrow
- **Transaction (2023-02-09):** Funds originated from Zeig IOTA Escrow, moved through accounts #2304977980 and #2000043165557, then dispersed to YBH Holdings LLC, Eisenstein Buyers, and layered offshore accounts. UETR and dollar amounts remain pending a subpoena from Banesco USA.
- **Suspicious Activity:** Wire fraud (escrow diversion), money laundering (layering), structuring. Narrative references IC3 Submission ID 7065f60922b948a59af3a8654edb16dd.
- **Attachment:** Consolidated_SAR_Report_IC3_7065f60922b948a59af3a8654edb16dd.pdf (annex with transaction tables, flowchart, compliance recommendations, and embedded subpoena request)

## Statement of Damages Overview
See [`STATEMENT OF DAMAGES.MD`](STATEMENT%20OF%20DAMAGES.MD) for the full claim narrative. Key figures include:

- **Unauthorized escrow diversion:** $256,693.68 in funds moved without proper instruction.
- **Treble damages exposure:** $1,026,774.72 under Fla. Stat. §772.11, based on tripling the diverted escrow amount.
- **Additional penalties estimate:** $100,950.00 in IRS-linked fines and interest tied to reporting failures.
- **Total known diverted funds:** Approximately $617,693.68 traced across Zeig PLLC IOTA escrow, Hasia Bitton, and YBH Holdings accounts.
- **Property & seller reference:** Land Trust Service Corporation, as trustee for Trust No. 2763-196, regarding 2763 NW 196 Terrace, Miami Gardens, FL 33056.

The statement also documents breach findings against Zeig Law Firm PLLC, enumerates fraud indicators (including spoofed instructions and unreported transfers), and asserts liens over all traced assets and related trust interests.
