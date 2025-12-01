# Copilot Instructions

## Paths to Reference
- `analysis.md`
- `sar_parser`

## Validation Commands
- `python -m pytest`

## CI Snippet for GitHub Actions
```yaml
name: CI

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Run validation commands
        run: |
          python -m pytest
```

## Owner Contact
For any inquiries, please reach out to Angela Henlon.
