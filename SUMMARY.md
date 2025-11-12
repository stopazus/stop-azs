# Stop AZS dataset quick reference

## Key files

- [`README.md`](README.md) – high-level overview of the escrow diversion dataset, usage guidance, and command snippets for subpoena coordination.
- [`README_EXTRA.md`](README_EXTRA.md) – supplemental operational guidance for investigators maintaining follow-up procedures and institution escalations.
- [`analysis.md`](analysis.md) – narrative summary of the confirmed transactions, pending subpoenas, evidence trail, and briefing shortcuts.
- [`data/network.json`](data/network.json) – structured investigative dataset containing SAR-aligned entities, properties, transactions, indicators, affidavits, communications, and bank follow-up directives.

## Validation commands

Run these from the repository root to verify the JSON structure or extract the preserved Received-path metadata:

```bash
python -m json.tool data/network.json
jq '.communications[] | select(.id|startswith("banesco-advice-")) | {id, received_chain_keys}' data/network.json
```

## Testing expectations

Because the repository is data-only, the validation commands above double as the expected "tests" prior to sharing updates:

1. `python -m json.tool data/network.json` confirms the investigative dataset remains well-formed JSON.
2. `jq '.communications[] | select(.id|startswith("banesco-advice-")) | {id, received_chain_keys}' data/network.json` reprints the parsed Banesco advice-of-debit routing chains to ensure subpoena-ready metadata is intact.
