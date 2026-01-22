# Project Overview

This README provides information about the project and instructions for contributors.

## Project Details

| Field | Value |
|---|---|
| Project ID | READMETX10002 |
| Date/Time (UTC) | 2025-01-12T17:41:39Z |
| Date (Local) | 1/12/2025 |
| Transaction Type | WIRE |
| Amount | 248500 |
| Direction | OUT |
| Originator/Beneficiary | YBH 2948 LLC |
| Originator Bank | OptimumBank |
| Originator SWIFT/BIC | OPTMUS3X |
| Beneficiary | Zeig Law PLLC IOTA |
| Beneficiary Bank | City National Bank (CNB) |
| Beneficiary SWIFT/BIC | CNBUS33 |
| File Reference 1 | FILE-24-981 |
| File Reference 2 | FILE-24-981-D1 |
| Description | Disbursement per instruction – File 24-981 |
| Flag 1 | TRUE |
| Flag 2 | TRUE |
| Flag 3 | TRUE |
| Flag 4 | TRUE |
| Status | passed |
| Verification | originator/beneficiary on file |
| Category | Treasury/Wires |
| Review Date | 2025-10-20T00:00:00Z |

## Contributing

Thanks for helping out! Do these one-time steps to get a clean local setup.

### 1) Prerequisites
- `jq` (required) — macOS: `brew install jq` · Ubuntu: `sudo apt-get install jq`
- `zsh` (recommended)
- `watch` (optional) — macOS: `brew install watch`
- `shellcheck` (for lint) — macOS: `brew install shellcheck` · Ubuntu: `sudo apt-get install shellcheck`

### 2) Create a virtual environment
Create a virtual environment using the interpreter available on your platform.

```sh
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

```powershell
# Windows PowerShell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 3) Install development dependencies
Install the tools used during development (currently just `pytest`). Keeping
them in `requirements-dev.txt` makes it easy to sync with CI.

```sh
python -m pip install -r requirements-dev.txt
```

### 4) Run local checks
```sh
# Execute the unit tests
pytest

# Optional: try the validator in an interactive Python session to see example errors
python - <<'PY'
from sar_parser.validator import validate_string

result = validate_string("""
<SAR>
  <FilingInformation>
    <ActivityAssociationTypeCode>Y</ActivityAssociationTypeCode>
  </FilingInformation>
</SAR>
""")
print("Valid?", result.is_valid)
for error in result.errors:
    print(f"- {error.message} ({error.xpath})")
PY
```

### CI (what runs on PRs)
- **Tests:** `pytest`
- **Concurrency:** new pushes cancel older runs for the same PR/branch.
