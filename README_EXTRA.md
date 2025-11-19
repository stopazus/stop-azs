# Stop AZS Investigative Operations Guide

This supplemental README expands on the quick brief in `README.md` and is
intended for analysts who need detailed instructions for maintaining and
using the Stop AZS escrow-diversion dataset.

## 1. Repository orientation

- **`README.md`** — high-level overview of the incident and quick usage
  notes.
- **`README_EXTRA.md`** (this file) — extended guidance, contact points,
  and operating procedures.
- **`data/network.json`** — canonical investigative dataset aligned to
  the SAR narrative, affidavit, information-sink checkpoints, bank
  follow-up directives, and preserved Banesco advice-of-debit headers.

Use any JSON-capable environment (Python, jq, notebooks, case management
tooling) to parse and present the dataset to investigators.
The dataset now advertises reusable `jq` commands in the
`command_snippets` section for quick validation or export tasks.

## 2. Working with the dataset

- Keep a local JSON validator (such as `jq`, `json.tool`, or IDE
  integration) handy to confirm edits before committing changes.
- Use notebooks or scripts to pivot the `transactions`,
  `pending_transactions`, and `information_sink` lists into case-ready
  tables.
- When referencing subpoena follow-up with Banesco USA, cite the stored
  advice-of-debit header chain (Message-IDs ending in
  `JavaMail.service_gftapp@VM-P-FISGFT`) to anchor requests for unique
  end-to-end reference numbers.
- On Windows workstations, run `jq '.' data/network.json >
  D:\\ICLOUD\\stop-azs-network.json` to keep a prettified working copy in
  shared evidence directories without modifying the original file.

## 3. Inspecting key sections

- **Transactions** enumerate confirmed wires and subpoena-dependent
  trails. The `pending_transactions` entry for 2023-02-09 still requires
  UETR confirmation from Banesco USA.
- **Entities and properties** catalog corporate and individual subjects,
  including the verified alias connecting 2733 NW 198th Terrace to the
  primary Miami Gardens address.
- **Attachments** identify the exhibits supplied with the SAR narrative.
- **Bank follow-up directives** describe the specific account records,
  KYC files, and ledgers to demand from Banesco USA and City National
  Bank of Florida.
- **Communications** preserve the Banesco advice-of-debit headers,
  parsed Received-path hop keys (from host, IP, protocol, timestamp),
  and routing metadata so investigators can cite precise relay details
  when escalating.
- **Information sink** distinguishes verified checkpoints from gaps
  still awaiting evidence.
- **Affidavit coverage** confirms Sharon Topaz's authority and the legal
  framework governing investigative actions.

## 4. Updating the dataset

1. Edit `data/network.json` to add new transactions, entities, or
   exhibits. Preserve existing keys so downstream tooling continues to
   parse the content.
2. For every new gap discovered, populate both the relevant section
   (e.g., `pending_transactions`, `law_enforcement_contacts`) and the
   `information_sink` to maintain traceability.
3. If new affidavit or authorization language is added, update the
   `affidavit` block and include a short description for each supporting
   document.
4. Validate the JSON structure after edits using `jq`, `python -m
   json.tool data/network.json`, or equivalent tooling before committing.

## 5. Evidence management checklist

- Store PDFs referenced in `data/network.json` in a controlled evidence
  repository; only filenames are captured here for chain-of-custody
  awareness.
- Ensure subpoena responses are logged with timestamps and financial
  institution reference numbers before updating the dataset.
- Confirm that any new properties include official parcel IDs or
  recorder references to streamline future tracing.

## 6. Escalation contacts

Coordinate rapid follow-up through the documented channels:

- **FBI – Internet Crime Complaint Center (IC3)**, Recovery Asset Team
  (RAT). Reference: `IC3 Submission ID: 7065f60922b948a59af3a8654edb16dd`.
- **FinCEN – BSA E-Filing**, Suspicious Activity Report (SAR) program.
- **IRS – Criminal Investigation (IRS-CI)**, Fraud / Money Laundering
  Referral program.

Include the 2023-01-11 wire (Banesco USA → City National Bank of
Florida, $206,693.68, OBI `22S-213 SELLER PROCEEDS 2763 NW 196 TERR`) in
all correspondence to expedite asset-freeze coordination.

## 7. Bank response procedures

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

## 8. Adding new guidance

When additional investigative procedures or partner requirements emerge,
append them to this file with a new numbered section so that all
investigators operate from the same playbook.

## 9. Command snippets reference

Consult the `command_snippets` block at the end of `data/network.json`
for ready-to-run helpers (execute them from the repository root so the
relative paths resolve correctly), including:

- `jq '.' data/network.json` — quick structure validation in any shell.
- `python -m json.tool data/network.json` — alternative Python-based
  check for environments without `jq`.
- `jq '.communications[] | select(.id=="banesco-advice-2023-02-09") |
  .received_chain_keys' data/network.json` — extracts the parsed
  Received-path hop metadata for the February 2023 Banesco email to quote
  during escalations.
- `jq '.communications[] | select(.id=="banesco-advice-2023-01-11") |
  .received_chain_keys' data/network.json` — companion command for the
  January 2023 Banesco advice-of-debit message when referencing earlier
  subpoena correspondence.
- `jq '.communications[] | select(.id|startswith("banesco-advice-")) |
  {id, received_chain_keys}' data/network.json` — consolidated view that
  prints both Banesco advice-of-debit chains with their identifiers when
  preparing subpoena packets.

Keep these commands handy so subpoena teams can pivot between the
February escalation trail and the January precursor without re-creating
the filters or overlooking the consolidated output.
