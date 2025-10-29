# stop-azs

This repository provides small utilities for exploring the [MITRE ATLAS](https://atlas.mitre.org/matrices/ATLAS) matrix. The
`stop_azs` package can download the official `ATLAS.yaml` dataset published by MITRE, group techniques by their tactics, and
summarise the number of techniques for each tactic.

## Installation

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The module can be used either as a library or as a small command line tool:

```bash
python -m stop_azs.atlas
```

This downloads the latest ATLAS dataset and prints the number of techniques that map to each tactic. In code you can use the
module like so:

```python
from stop_azs import load_atlas_data, select_matrix, group_techniques_by_tactic, summarise_matrix

data = load_atlas_data()
matrix = select_matrix(data)
grouped = group_techniques_by_tactic(matrix)
summary = summarise_matrix(grouped)
```

`grouped` is an ordered dictionary mapping tactic names to lists of `Technique` objects. Each `Technique` exposes a
`display_name()` helper that prefixes subtechniques with their parent technique name when available.
