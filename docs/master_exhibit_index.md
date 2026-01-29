# Master Exhibit Index

The Master Exhibit Index (MEI) is a centralized registry of all exhibits filed with law enforcement agencies (FBI IC3, FinCEN, IRS-CI) in the escrow diversion investigation. It provides a structured, machine-readable catalog of evidence submitted in support of the case.

## Purpose

The MEI serves multiple purposes:
* Provides a single source of truth for all filed exhibits
* Tracks filing status and Bates numbering for each exhibit
* Records cryptographic hashes and metadata for evidence integrity
* Enables programmatic access to exhibit information for reporting and analysis

## Structure

The MEI is stored as a JSON file (`master_exhibit_index.json`) at the repository root. Each exhibit entry contains:

### Required Fields

* **exhibit_id**: Unique identifier for the exhibit (e.g., "A", "B", "E-1")
* **title**: Human-readable title describing the exhibit contents
* **status**: Filing status (e.g., "Filed", "Verified / Filed", "Pending")
* **bates_range**: Bates number range for the exhibit (e.g., "NST-A-0001 → NST-A-0015")

### Optional Fields

* **file_name**: Name of the PDF or document file
* **sha256_hash**: SHA-256 cryptographic hash of the file for integrity verification
* **prepared_by**: Entity or person who prepared the exhibit
* **prepared_date**: Date the exhibit was prepared (ISO 8601 format: YYYY-MM-DD)
* **notes**: Additional notes or context about the exhibit

## Example

```json
{
    "Master_Exhibit_Index": [
        {
            "exhibit_id": "A",
            "title": "IC3 Complaint and Supporting Evidence",
            "status": "Filed",
            "bates_range": "NST-A-0001 → NST-A-0015"
        },
        {
            "exhibit_id": "E-1",
            "title": "Wire Disbursement TX10002 (OptimumBank → CNB / Zeig Law PLLC IOTA)",
            "bates_range": "NST-E1-0001 → NST-E1-0003",
            "file_name": "Exhibit_E1_Wire_Disbursement_TX10002_Bates.pdf",
            "sha256_hash": "44015903de5e37fd918a474aad22fcce8bcb455c7d2caa7259d792cacf4cdf91",
            "prepared_by": "N & S Holding LLC",
            "prepared_date": "2025-10-20",
            "status": "Verified / Filed",
            "notes": "Disbursement per FILE‑24‑981 instruction, verified compliance and sanctions screening passed."
        }
    ]
}
```

## Python API

The `exhibit_index.py` module provides a Python API for working with the MEI:

```python
from exhibit_index import load_master_exhibit_index

# Load the index
index = load_master_exhibit_index()

# Get all filed exhibits
filed = index.get_filed_exhibits()

# Get a specific exhibit by ID
exhibit_a = index.get_exhibit_by_id("A")
if exhibit_a:
    print(f"Title: {exhibit_a.title}")
    print(f"Status: {exhibit_a.status}")
    print(f"Bates Range: {exhibit_a.bates_range}")
```

## Current Exhibits

The Master Exhibit Index currently tracks the following exhibits:

* **Exhibit A**: IC3 Complaint and Supporting Evidence (NST-A-0001 → NST-A-0015)
* **Exhibit B**: Legal Claims Summary and Property Ownership Timeline (NST-B-0001 → NST-B-0006)
* **Exhibit C**: Advice of Debit – Bank Confidential and Escrow Instructions (NST-C-0001 → NST-C-0004)
* **Exhibit D**: Layering Activity and SAR Narrative Report (NST-D-0001 → NST-D-0005)
* **Exhibit E-1**: Wire Disbursement TX10002 (OptimumBank → CNB / Zeig Law PLLC IOTA) (NST-E1-0001 → NST-E1-0003)

All exhibits are currently in "Filed" or "Verified / Filed" status.

## Maintenance

When adding new exhibits to the MEI:

1. Add the exhibit entry to `master_exhibit_index.json` with all required fields
2. Include optional fields (file_name, sha256_hash, etc.) when available
3. Verify the JSON syntax is valid
4. Run tests to ensure integrity: `python3 tests/test_exhibit_index.py`
5. Update this documentation if the exhibit structure changes

## Integration

The MEI integrates with other tools in the repository:

* Can be referenced in `analysis.md` for exhibit citations
* Complements the `tools/aml_exhibit_builder.py` for creating new exhibits
* Provides structured data for automated reporting and filing workflows
