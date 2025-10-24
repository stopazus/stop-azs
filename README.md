# stop-azs

`stop-azs` is a tiny Python utility for cleaning lists of cloud availability zones.
It can be imported as a library or executed from the command line to deduplicate
zones before provisioning infrastructure.

## Features

- Detect duplicate zones in a case-insensitive manner while preserving the first
  observed capitalisation.
- Remove duplicates without reordering the original data.
- Produce machine-friendly summaries for reporting or downstream automation.

## Installation

```bash
pip install .
```

## Usage

Create a text file that contains the availability zones you want to analyse,
one per line, and run the CLI:

```bash
stop-azs zones.txt
```

To view a summary instead of the cleaned list:

```bash
stop-azs --summary zones.txt
```

Or to print only the duplicate entries:

```bash
stop-azs --duplicates zones.txt
```

The core functionality is also available as Python functions:

```python
from stop_azs import find_duplicate_zones, remove_duplicate_zones

zones = ["us-east-1a", "us-east-1A", "us-east-1b"]
print(find_duplicate_zones(zones))  # ["us-east-1a"]
print(remove_duplicate_zones(zones))  # ["us-east-1a", "us-east-1b"]
```

## Development

Install the project in editable mode and run the tests:

```bash
pip install -e '.[test]'
pytest
```
