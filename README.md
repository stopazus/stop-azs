# stop-azs
This repository documents key allegations and participants in the alleged diversion of escrow funds
from the City National Bank trust account controlled by Justin E. Zeig. See [analysis.md](analysis.md)
for detailed background on the trust account activity, summaries of the shell entities involved,
captured case metadata, identified red flags, an expanded forensic ledger exhibit (as of 24 August
2025), and a concluding synthesis that ties the observed pass-through behavior to the ongoing
recovery and enforcement efforts.

## SAR Parser

The `sar_parser` module provides validation utilities for Suspicious Activity Report (SAR) XML documents that follow the FinCEN schema. The validator performs structural and semantic checks to surface actionable validation errors.

## Testing

The project includes automated tests for the SAR parser module. Run tests using:
```bash
python -m unittest discover tests/
```
