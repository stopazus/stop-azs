# Stop AZS Investigative Operations Guide

This supplemental README expands on the quick brief in `README.md` and is
intended for analysts who need detailed instructions for maintaining and
running the Stop AZS escrow-diversion dataset and briefing tooling.

## 1. Repository orientation

- **`README.md`** — high-level overview of the incident and quick usage
  snippet.
- **`README_EXTRA.md`** (this file) — extended guidance, contact points,
  and operating procedures.
- **`data/network.json`** — canonical investigative dataset aligned to
  the SAR narrative, affidavit, and information-sink checkpoints.
- **`analysis.py`** — briefing generator that parses the dataset and
  prints an investigator-ready summary.

## 2. Environment prerequisites

- Python 3.9 or newer.
- No third-party dependencies are required beyond the Python standard
  library. The helper script uses only `json`, `dataclasses`, and
  `pathlib`.

## 3. Running the briefing helper

From the repository root, execute:

```bash
python analysis.py
```

The script will emit:

1. Filing metadata (FinCEN SAR identifiers and submission context).
2. Confirmed transactions and subpoena-dependent trails.
3. Entity roster with roles, jurisdictions, and affidavit authority.
4. Property ledger, including verified and unverified addresses.
5. Attachment catalogue with descriptions for each exhibit.
6. Law-enforcement contacts and requested actions.
7. Bank-response directives that describe how to push institutions for
   complete customer records.
8. Outstanding gaps, annotated when a dependency already lives in the
   information sink.
9. Verified checkpoints sourced from the `information_sink` section to
   highlight evidence-backed statements.

## 4. Interpreting the output

- **Transactions** list both confirmed wires and any pending subpoenas;
  check for `Amount pending` or `UETR` placeholders that require bank
  follow-up.
- **Outstanding items** will explicitly call out missing EINs, account
  numbers, property verification, and attachment metadata. When a gap is
  already noted in the information sink, the message is labelled so
  investigators can reuse the documented dependency.
- **Bank follow-up directives** outline which institutions to press and
  the categories of records to demand. Use these prompts to keep
  requesting information until every customer involved in the diversion
  is documented.
- **Information sink** entries enumerate which items are verified, which
  are awaiting subpoenas, and which require additional confirmation from
  counterparties.
- **Affidavit coverage** confirms the authority of Sharon Topaz and the
  compliance statutes that govern investigative actions.

## 5. Updating the dataset

1. Edit `data/network.json` to add new transactions, entities, or
   exhibits. Preserve existing keys so the helper continues to parse the
   content.
2. For every new gap discovered, populate both the relevant section
   (e.g., `pending_transactions`, `law_enforcement_contacts`) and the
   `information_sink` to maintain traceability.
3. If new affidavit or authorization language is added, update the
   `affidavit` block and include a short description for each supporting
   document.
4. Run `python analysis.py` after edits to validate the JSON structure
   and confirm the output renders as expected.

## 6. Evidence management checklist

- Store PDFs referenced in `data/network.json` in a controlled evidence
  repository; only filenames are captured here for chain-of-custody
  awareness.
- Ensure subpoena responses are logged with timestamps and financial
  institution reference numbers before updating the dataset.
- Confirm that any new properties include official parcel IDs or
  recorder references to streamline future tracing.

## 7. Escalation contacts

Coordinate rapid follow-up through the documented channels:

- **FBI – Internet Crime Complaint Center (IC3)**, Recovery Asset Team
  (RAT). Reference: `IC3 Submission ID: 7065f60922b948a59af3a8654edb16dd`.
- **FinCEN – BSA E-Filing**, Suspicious Activity Report (SAR) program.
- **IRS – Criminal Investigation (IRS-CI)**, Fraud / Money Laundering
  Referral program.

Include the 2023-01-11 wire (Banesco USA → City National Bank of
Florida, $206,693.68, OBI `22S-213 SELLER PROCEEDS 2763 NW 196 TERR`) in
all correspondence to expedite asset-freeze coordination.

## 8. Bank response procedures

The `bank_follow_up` block in `data/network.json` captures standing
instructions whenever Banesco USA or City National Bank of Florida
replies. Always request:

- Comprehensive transaction histories for every customer tied to the
  diverted escrow period, not just the flagged accounts.
- KYC files, signature cards, disbursement authorizations, and compliance
  review notes for all related customers.
- SWIFT/ACH logs, client ledgers, and any narrative fields explaining how
  funds were applied or redistributed.

If the institution omits any identifiers or supporting documents, issue
follow-up questions that enumerate the missing fields and keep the case
log updated until the response is complete.

## 9. Adding new guidance

When additional investigative procedures or partner requirements emerge,
append them to this file with a new numbered section so that all
investigators operate from the same playbook.

