# Copilot Instructions

## Paths to Reference
- `analysis.md`
- `sar_parser`

## Validation Commands
Please ensure to run the following commands to validate:
- `yarn lint`
- `yarn test`

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

      - name: Install dependencies
        run: yarn install

      - name: Run validation commands
        run: |
          yarn lint
          yarn test
```

## Owner Contact
For any inquiries, please reach out to Angela Henlon.