# Audit Notes

## Potential Typo
- `README.md` mixes American and British spellings: the features list says "Normalises" even though the rest of the documentation (for example the CLI section) uses American English such as "Analyze". Standardise to "Normalizes" for consistency.

## Bug
- `Transaction.from_dict` in `src/stop_azs/analyzer.py` coerces identifiers with `str(pop_any(...) or "")`. This treats legitimate falsy values like `0` as missing and raises an error instead of accepting them. Adjust the logic to only fall back when the helper returns `None` so numeric references or senders of `"0"` are accepted. 【F:src/stop_azs/analyzer.py†L39-L52】

## Documentation Discrepancy
- The docstring for `load_transactions` claims it only supports "CSV or JSON", but the implementation also handles newline-delimited JSON (`.ndjson`). Update the docstring (and related help text in `cli.py`) to reflect NDJSON support. 【F:src/stop_azs/analyzer.py†L136-L170】【F:src/stop_azs/cli.py†L14-L34】

## Test Improvement
- `test_repeated_invoice_counts_unique_senders` in `tests/test_analyzer.py` only inspects the first flagged transaction, so regressions where later entries miss the `REPEATED_INVOICE` flag would slip by. Strengthen the assertion to verify every transaction sharing the invoice is flagged. 【F:tests/test_analyzer.py†L25-L36】
