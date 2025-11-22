# Copilot Instructions

## Paths to Reference
- `analysis.md`
- `sar_parser`

## Validation Commands
Please ensure to run the following commands to validate:
- `python3 -m flake8 sar_parser tests --count --select=E9,F63,F7,F82 --show-source --statistics`
- `python3 -m unittest discover tests -v`

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
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install flake8

      - name: Run validation commands
        run: |
          python3 -m flake8 sar_parser tests --count --select=E9,F63,F7,F82 --show-source --statistics
          python3 -m unittest discover tests -v
```

## Owner Contact
For any inquiries, please reach out to Angela Henlon.