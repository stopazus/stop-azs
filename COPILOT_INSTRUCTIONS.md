# Copilot Instructions

## Paths to Reference
- `analysis.md`
- `sar_parser`

## Validation Commands
Please ensure to run the following commands to validate:
- `python -m py_compile sar_parser/*.py tests/*.py`
- `python tests/test_validator.py`

## CI Snippet for GitHub Actions
```yaml
name: Python CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run validation commands
        run: |
          python -m py_compile sar_parser/*.py tests/*.py
          python tests/test_validator.py
```

## Owner Contact
For any inquiries, please reach out to Angela Henlon.