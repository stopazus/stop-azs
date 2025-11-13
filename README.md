# Stop AZS Escrow Diversion Dataset

This repository preserves the data points shared with investigators about
the diversion of $206,693.68 in sale proceeds owed to **N & S Holding
LLC**. The dataset mirrors the suspicious activity narrative submitted to
the FBI's Internet Crime Complaint Center (IC3) and related SAR
supplements, including the confirmed 2023-01-11 wire to the Zeig Law
Firm PLLC IOTA account at City National Bank of Florida.

## Repository contents

- `data/network.json` – structured representation of the IC3 submission,
  the confirmed wire details, entities, properties (including the
  clarified 2733 NW 198th Terrace alias for 2763 NW 196 Terrace),
  red-flag indicators, the affidavit of authorized representative,
  law-enforcement touchpoints, exhibit references, bank-response follow
  up directives, and the captured Banesco advice-of-debit email headers
  with parsed Received-path keys for subpoena coordination.
- `README_EXTRA.md` – supplemental operational guidance for investigators
  maintaining the dataset and escalating follow-up with involved
  institutions.
- `SUMMARY.md` – quick reference for key repository files along with the
  validation commands investigators should run before sharing updates.
- `analysis.md` – narrative briefing that synthesizes confirmed activity,
  pending follow-ups, preserved evidence, and command shortcuts for
  subpoena preparation.

## Usage

The repository is data-only. Load `data/network.json` with your analysis
tooling (for example, `jq`, a notebook, or case-management platform) to
review:

1. Filing metadata and the verified 2023-01-11 Banesco \u2192 City National
   Bank of Florida wire.
2. Pending subpoena trails that still require unique end-to-end (UETR)
   identifiers or beneficiary account numbers.
3. Entities, properties, red-flag indicators, affidavits, and law-
   enforcement contacts aligned to the SAR narrative.
4. Bank follow-up directives, including the newly preserved Banesco
   advice-of-debit email headers and their parsed Received-path keys to
   cite when requesting full transaction histories and UETR values.
5. Verified checkpoints and information-sink gaps that document which
   dependencies remain outstanding.

### Quick Windows export example

- Open a PowerShell prompt where the repository is available.
- Run `jq '.' data/network.json > D:\\ICLOUD\\stop-azs-network.json` to
  create a prettified copy alongside any Windows evidence folders.
- Reference the `command_snippets` block at the end of
  `data/network.json` for additional ready-to-run validation and
  Received-path extraction commands covering the January and February
  Banesco advice-of-debit emails.

### Command snippet highlights

Use these ready-to-copy helpers (also recorded under
`command_snippets` inside `data/network.json`) from the repository
root when briefing or coordinating subpoenas:

- `jq '.communications[] | select(.id=="banesco-advice-2023-02-09") | .received_chain_keys' data/network.json`
  &mdash; prints the parsed hop metadata for the February 2023 Banesco
  advice-of-debit email.
- `jq '.communications[] | select(.id=="banesco-advice-2023-01-11") | .received_chain_keys' data/network.json`
  &mdash; companion helper for the January 2023 Banesco advice-of-debit
  chain so investigators can cite the earlier routing details.
- `jq '.communications[] | select(.id|startswith("banesco-advice-")) | {id, received_chain_keys}' data/network.json`
  &mdash; consolidated view that prints both Banesco advice-of-debit
  chains with their identifiers when preparing subpoena packets.

### Color cue legend

The investigative brief and dataset reference two color cues for fast
status checks:

- **White** entries call out evidence-backed checkpoints that already
  have corroborating documentation.
- **Red** entries flag unresolved subpoenas or missing records that
  still require escalation.

No blue state is used in this workflow so investigators can focus on
the verified (white) and outstanding (red) streams without ambiguity.

## Current commit summary

- Extended `data/network.json` with parsed Banesco advice-of-debit
  Received-path keys and ready-to-run `jq` helpers for both January and
  February communications so investigators can quote individual hops
  when demanding UETR confirmations.
- Updated `README.md` and `README_EXTRA.md` to reflect the data-only
  repository layout, the new communications capture, and the expanded
  command snippets.
- Added `analysis.md` as a narrative companion to `data/network.json`
  summarizing confirmed transactions, outstanding subpoenas, and the
  available evidence trail.
- Introduced `SUMMARY.md` so investigators have a concise Markdown
  checklist of key files and the validation commands to rerun after
  editing the dataset.

### Validation

- Not applicable (no executable tooling in repository)
