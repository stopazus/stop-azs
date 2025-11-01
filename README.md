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

## Current commit summary

- Extended `data/network.json` with parsed Banesco advice-of-debit
  Received-path keys so investigators can reference individual hops when
  demanding UETR confirmations.
- Updated `README.md` and `README_EXTRA.md` to reflect the data-only
  repository layout and the new communications capture.

### Validation

- Not applicable (no executable tooling in repository)
