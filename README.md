Stop AZS — Investigative Dataset for Escrow Diversion

Purpose
-------
This repository preserves and organizes the investigative data and supporting references for a confirmed escrow-diversion event involving a $206,693.68 wire (Banesco USA → City National Bank of Florida) referenced in the IC3 submission and related SAR materials. The dataset is intended for use by investigators to validate timelines, request follow-up from financial institutions, and maintain an auditable record of case artifacts.

What's in this repository
-------------------------
- data/network.json — Canonical, structured investigative dataset: transactions (confirmed and pending), entities and properties, attachments (exhibit filenames), bank follow-up directives, preserved communications headers, affidavit text, law-enforcement touchpoints, red-flag indicators, and an information-sink that documents outstanding evidence gaps.
- README_EXTRA.md — Extended operational guidance, escalation contacts, evidence-management checklist, and command-snippet helpers for investigators and analysts.
- (Other files) — Any referenced exhibits or evidence PDFs should be stored in a controlled evidence repository; only filenames are referenced in data/network.json.

Quick usage
-----------
- Inspect and validate:
  - jq '.' data/network.json
  - python -m json.tool data/network.json
- Export a prettified copy on Windows:
  - Open PowerShell where the repository is checked out and run:
    jq '.' data/network.json > D:\ICLOUD\stop-azs-network.json
- Extract Banesco advice-of-debit parsed Received-path hop keys (example):
  - jq '.communications[] | select(.id=="banesco-advice-2023-02-09") | .received_chain_keys' data/network.json

Recommended workflow
--------------------
1. Use the dataset as the canonical source for timelines and bank escalation requests.
2. When issuing subpoenas or follow-ups, cite identifiers preserved in data/network.json (e.g., Message-IDs, OBI values, IC3 Submission ID).
3. Log all subpoena responses and update data/network.json only after verifying the response and validating JSON structure (jq or python json.tool).
4. Add any newly discovered evidence or gaps to both the relevant section (transactions, pending_transactions, bank_follow_up, etc.) and the information_sink block to preserve traceability.

Bank follow-up guidance (summary)
--------------------------------
Always request from responding financial institutions:
- Full transaction histories for implicated customers during the diversion window.
- UETR or unique end-to-end identifiers for wire messages and any correspondent-bank references.
- KYC documentation, signature cards, disbursement authorizations, internal compliance notes, and client ledgers or narrative fields that explain fund flows.
- SWIFT/ACH logs and any additional identifiers omitted from initial replies; enumerate missing fields if incomplete.

Escalation contacts (summary)
-----------------------------
- FBI — Internet Crime Complaint Center (IC3) Recovery Asset Team (use IC3 Submission ID recorded in data/network.json).
- FinCEN — BSA E-Filing / SAR program.
- IRS — Criminal Investigation (IRS-CI), Fraud / Money Laundering referral channels.

Maintaining the dataset
-----------------------
- Keep only filenames in this repository for evidentiary artifacts. Store actual PDFs and binary evidence in an evidence repository or secure case management system with chain-of-custody controls.
- Validate JSON before committing:
  - jq '.' data/network.json
  - python -m json.tool data/network.json
- When adding new guidance, append a numbered section to README_EXTRA.md so all investigators follow a consistent playbook.

Privacy and handling
--------------------
This repository may contain or reference sensitive investigative data. Restrict repository access to authorized personnel only and follow local policies for evidence handling and disclosure. Do not publish or share raw evidence files outside of secure case-management systems.

Change log / commit message guidance
-----------------------------------
When updating this repository, use clear commit messages that describe:
- What was added or changed (e.g., "Add subpoena response from Banesco; update pending_transactions UETR").
- Which case artifact or exhibit was added (reference filename).
- Any actions required by downstream analysts (e.g., "Follow up: request UETR from Banesco for 2023-02-09 transaction").
