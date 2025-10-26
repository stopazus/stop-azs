# stop-azs

This repository tracks compliance and risk artifacts for N &amp; S Holding LLC. It contains:

- A connector manifest under `data/` describing available third-party integrations and the environment variables required to activate them.
- Suspicious Activity Report (SAR) source files under `reports/sar/` that mirror the latest regulatory filings.

## Data catalog

| Path | Description |
| --- | --- |
| `data/n_s_holding_llc.json` | Integration manifest for sanctions, lien, property-title, payment connectors, and escalation contacts. |
| `data/evidence_manifest.csv` | Hash and custody metadata for external evidence supporting the SAR narrative. |
| `reports/sar/2025-09-11_initial.xml` | XML SAR prepared for the 2025-09-11 initial filing (FinCEN schema v1.5). |

## Usage notes

- Secrets such as API keys or webhook tokens must be stored in environment variables (for example, `.env` files or a secrets vault) and **must not** be committed to this repository.
- The SAR XML is intentionally stored as received; update the `Amount` and `UETR` fields once subpoena responses are available.
- Evidence artifacts listed in `data/evidence_manifest.csv` remain in secure storage (see `source_path` references) and should be pulled from `/mnt/data/` using the recorded SHA-256 digests before inclusion in any regulatory submission package.

## Escalation contacts

Coordinate regulatory or law-enforcement follow-up through the escalation contacts embedded in `data/n_s_holding_llc.json`:

- **FBI – Internet Crime Complaint Center (IC3)**, Recovery Asset Team (RAT); cite IC3 Submission ID `7065f60922b948a59af3a8654edb16dd` when requesting assistance.
- **FinCEN – BSA E-Filing**, Suspicious Activity Report (SAR) program support for amendments or supplemental filings.
- **IRS – Criminal Investigation (IRS-CI)**, Fraud / Money Laundering Referral program for tax-implicated recovery actions.
