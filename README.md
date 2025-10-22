# Stop AZS Escrow Diversion Dataset

This repository preserves the data points shared with investigators about
the diversion of $206,693.68 in sale proceeds owed to **N & S Holding
LLC**. The dataset mirrors the suspicious activity narrative submitted to
the FBI's Internet Crime Complaint Center (IC3) and related SAR
supplements, including the confirmed 2023-01-11 wire to the Zeig Law
Firm PLLC IOTA account at City National Bank of Florida.

## Repository contents

- `data/network.json` – structured representation of the IC3 submission,
  the confirmed wire details, entities, properties, red-flag indicators,
  the affidavit of authorized representative, law-enforcement
  touchpoints, and exhibit references.
- `analysis.py` – helper script that loads the dataset and prints a
  briefing-ready synopsis covering the FinCEN filing details, the
  recorded wire, subpoena-dependent activity, data gaps that still need
  subpoenas, associated entities, indicators, and requested actions. It
  also calls out missing jurisdiction or role information for any
  entities, properties that remain unverified, attachments without
  descriptions, and law-enforcement contacts awaiting reference or
  action details so investigators can chase those gaps.

## Usage

Run the analysis helper to generate a plain-text briefing:

```bash
python analysis.py
```

The script confirms the known $206,693.68 escrow diversion, outlines the
FinCEN submission metadata, lists the pending subpoena-driven tracing
items, enumerates unresolved data gaps (such as missing EIN, UETR,
entity roles or jurisdictions, unverified properties, attachment
descriptions, or law-enforcement reference numbers), summarizes the
related entities and properties, surfaces the affidavit authority and
compliance statements, and restates the red-flag indicators and
law-enforcement requests included with the SAR narrative.
