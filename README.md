# stop-azs

Command-line utility for validating Suspicious Activity Report (SAR) XML filings. The
validator focuses on catching common data-quality problems such as malformed XML,
placeholder values, and future-dated filings.

## Installation

Create a virtual environment and install the package in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

To validate every SAR XML file within a directory and export a JSON report:

```bash
python -m stop_azs.cli --validate-dir ./sar_files --export-report report.json
```

If you only need console output, omit the `--export-report` argument. The command exits with
status code `0` when no errors are detected and `2` when one or more errors are found.

## Development

Install the optional testing dependencies and run the test suite with `pytest`:

```bash
pip install -e .[test]
pytest
```
