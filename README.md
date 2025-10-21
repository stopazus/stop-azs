# stop-azs

This repository contains a small utility for extracting a quick summary from a
FinCEN Suspicious Activity Report (SAR) XML document.  The parser is intentionally
lightweight – it only reads the most common metadata that investigators usually
need when triaging filings (filing information, subjects, and transactions).

## Usage

```
python sar_parser.py path/to/sar.xml
```

The script prints a JSON summary to standard output.  This allows the tool to be
piped into downstream systems or simply inspected by a human reviewer.

## Development

The project has no runtime dependencies beyond the Python standard library.  To
run the unit tests (which require `pytest`):

```
pip install pytest
pytest
```
