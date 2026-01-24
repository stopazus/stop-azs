# stop-azs

Tools for quickly surfacing potentially suspicious escrow transactions.  The
package is intentionally lightweight: it applies a handful of transparent
rules and produces a report that investigators can review alongside other
case material.  None of the flags should be interpreted as proof of
wrongdoing—they are merely prompts for deeper analysis.

## Features

- Normalizes escrow transactions captured in CSV, JSON, or NDJSON exports.
- Applies configurable heuristics such as large-value transfers, repeated
  invoice reuse, high-risk jurisdictions, and receivers that aggregate many
  senders.
- Produces either a human-readable table or machine-readable JSON payload.

## Installation

The project targets Python 3.11 or newer.  You can install the package in a
virtual environment with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

The optional ``dev`` dependencies install the ``pytest`` test runner.

## Usage

After installation the command line interface is available through
``python -m stop_azs.cli``.  To analyze the sample data bundled with the
repository:

```bash
python -m stop_azs.cli analyze examples/sample_transactions.csv \
  --domestic-country US \
  --high-risk-country GB \
  --large-amount-threshold 40000
```

The command prints a table highlighting the transactions that triggered one or
more heuristics, followed by a summary count of the flags.  Pass ``--output
json`` to receive the full result set in JSON format instead.

## Testing

Run the test-suite with:

```bash
pytest
```

## Data format

Transaction exports should include the columns listed below.  Additional
columns are preserved in the metadata payload and echoed in the JSON output.

| Column | Required | Notes |
| --- | --- | --- |
| ``reference`` | Yes | Unique identifier for the transfer. |
| ``sender`` | Yes | Originator name or account reference. |
| ``receiver`` | Yes | Beneficiary name or account reference. |
| ``amount`` | Yes | Numeric value, parsed as a decimal. |
| ``currency`` | No | Defaults to ``USD`` when omitted. |
| ``date`` | Yes | Supports ISO ``YYYY-MM-DD`` and common locale specific formats. |
| ``invoice_number`` | No | Used to detect reuse across senders. |
| ``destination_country`` | No | ISO country code. |

## Sample data

``examples/sample_transactions.csv`` contains a fabricated dataset that
illustrates each heuristic.  The data is fictional and exists solely for
integration testing and demonstrations.
