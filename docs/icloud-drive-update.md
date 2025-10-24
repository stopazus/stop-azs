# iCloud Drive Compliance Update

This document consolidates the data required to update the iCloud Drive workspace that houses the supporting material for the IC3 complaint referenced in the SAR narrative. Use this checklist to confirm that the shared drive contains complete artifacts and metadata for the investigation.

## Filing Snapshot

| Field | Value |
| --- | --- |
| Filing Type | Initial |
| Filing Date | 2025-09-11 |
| Contact Office | N & S Holding LLC - AML Surveillance Unit |
| Contact Phone | 786-707-7111 |
| Contact Email | office@nsholding.us |

## Subject Entities

| Entity Name | Type | Notes |
| --- | --- | --- |
| YBH Holdings LLC | Business | Beneficiary of diverted escrow funds. |
| Eisenstein Buyers | Business | Beneficiary of diverted escrow funds. |
| Zeig IOTA Escrow | Business | Originator of wire activity; escrow instructions allegedly diverted. |

## Transaction Summary

| Date | Amount (USD) | Originator | Pass-through Accounts | Beneficiaries | UETR | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 2023-02-09 | Pending subpoena response | Zeig IOTA Escrow | #2304977980, #2000043165557 | YBH Holdings LLC; Eisenstein Buyers; Layered offshore accounts | Pending | Routing inconsistent with escrow instructions; suspected layering/structuring. |

## Required iCloud Drive Artifacts

- **Consolidated SAR Report**: `Consolidated_SAR_Report_IC3_7065f60922b948a59af3a8654edb16dd.pdf`
  - Ensure that the PDF contains the annex with transaction tables, flowchart, compliance recommendations, and the embedded subpoena request.
- **IC3 Intake Confirmation**: Upload a copy of IC3 Submission ID `7065f60922b948a59af3a8654edb16dd` from iCloud Drive.
- **Bank Correspondence**: Add any subpoena or correspondence with Banesco USA regarding UETR and dollar amounts.
- **Escrow Instructions**: Include original escrow instructions to highlight routing discrepancies.
- **Pass-through Account Statements**: Secure statements for accounts `#2304977980` and `#2000043165557` covering activity in February 2023.

## Digital Evidence Manifest QA

The `SHA256_Manifest_7065f609.xlsx` workbook (Sheet1) tracks seven artifacts that should already exist in the iCloud Drive workspace. The latest review surfaced the following exceptions that must be cleared before the case packet can be considered complete:

- **Missing hashes**: All seven rows have empty or invalid values in the `sha_256_checksum` column. Compute a SHA-256 digest for each file using `shasum -a 256 <file>` (macOS) or `sha256sum <file>` (Windows PowerShell via WSL) and paste the 64-character lowercase result into the manifest.
- **Invalid formats**: Because the checksum column is blank, the manifest also fails the validation rules for hexadecimal formatting. After populating each digest, confirm there are no stray spaces or uppercase characters.
- **Timestamp verification**: Ensure the `generated_timestamp_(utc)` column reflects the time each artifact was last validated. If a file is updated after the digest is captured, recalculate the hash and refresh the timestamp.
- **Custodian/entity attribution**: Double-check the `custodian/entity` assignments to align with the subject list below (e.g., Zeig IOTA Escrow for originator documents, YBH Holdings LLC for beneficiary records).

Once the manifest is corrected, export a PDF snapshot and store both the XLSX and PDF versions in the case folder. Retain the original XLSX path in a `readme.txt` inside the evidence directory so future reviewers can locate the canonical spreadsheet quickly.

### Optional automation: `fill_hash_manifest.py`

The repository includes a helper script [`fill_hash_manifest.py`](../fill_hash_manifest.py) that reads `SHA256_Manifest_7065f609.xlsx`, calculates SHA-256 digests for any files listed in column A that exist beside the manifest, and fills the checksum and timestamp fields automatically.

1. Install the lone dependency with `pip install openpyxl` if it is not already available.
2. Place the script, the manifest, and all referenced evidence files in the same directory.
3. Run `python fill_hash_manifest.py` to populate the missing hashes and timestamps. Rows with missing files are left untouched for manual follow-up.
4. Re-open the manifest to confirm each row has the expected lowercase hash, a fresh UTC timestamp, and correct custodian assignments.

Re-export the PDF snapshot after the automated pass, then proceed with the archival steps above.

## Outstanding Items

- Confirm dollar amount and UETR identifier once Banesco USA responds to the subpoena.
- Verify whether any additional beneficiaries or offshore layering structures have been identified since the initial filing.
- Update the iCloud Drive folder sharing permissions to include the AML Surveillance Unit distribution list.

## Update Procedure

1. Sign in to the iCloud account associated with `office@nsholding.us`.
2. Open the iCloud Drive folder dedicated to the IC3 case `7065f60922b948a59af3a8654edb16dd`.
3. Upload any missing documents listed above and cross-check against the SAR filing snapshot.
4. Apply the folder tags `wire-fraud`, `escrow-diversion`, and `layering` so the workspace remains searchable across Apple devices.
5. Notify the AML Surveillance Unit once all artifacts are present and metadata is complete.

