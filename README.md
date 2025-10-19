# stop-azs

Utilities for inspecting suspicious activity report (SAR) transaction data.

## Installation

The project uses a standard Python layout. Install the package in editable mode
while developing:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

Use the command line interface to analyse transaction files:

```bash
python -m stop_azs.cli analyze path/to/transactions.ndjson
```

The `analyze` subcommand accepts CSV, JSON, and newline-delimited JSON (NDJSON)
files. For CSV inputs each row is treated as a transaction. For JSON inputs a
single top-level array is expected. NDJSON inputs should contain one JSON object
per line.

By default the command totals the values in the `amount` field. Use the
`--amount-field` option to specify a different column or object key:

```bash
python -m stop_azs.cli analyze data/transactions.csv --amount-field value
```
