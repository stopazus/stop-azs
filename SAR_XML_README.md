# SAR Supplement XML Documentation

This directory contains a Suspicious Activity Report (SAR) supplement in XML format along with its associated stylesheet.

## Files

- **SARSupplement_NORMALIZED.xml** - The SAR supplement data in XML format, conforming to the FinCEN SAR schema
- **sar_stylesheet.xsl** - XSL stylesheet for formatting the XML data for browser display

## Viewing the SAR Report

To view the formatted SAR report:

1. **In a Web Browser** (recommended):
   - Open `SARSupplement_NORMALIZED.xml` directly in a modern web browser (Chrome, Firefox, Safari, Edge)
   - The browser will automatically apply the XSL stylesheet and display a formatted, human-readable report
   - The report includes professional styling with tables, color-coded sections, and organized information

2. **Via GitHub Pages**:
   - If this repository is published via GitHub Pages, the XML file will be accessible at the repository URL
   - The browser will apply the stylesheet automatically when viewing the XML file

3. **As Raw XML**:
   - Use any text editor to view the raw XML structure
   - Useful for programmatic access or validation

## Data Source

The SAR supplement data is derived from the forensic analysis documented in `analysis.md`, which includes:
- Escrow diversion investigation metadata
- Transaction details from the City National Bank trust account
- Subject entities and individuals involved
- Property records and transaction timelines
- Red flag indicators for suspicious activity
- Law enforcement contact information

## Validation

The XML file has been validated against the SAR schema requirements using the `sar_parser` validation module:

```bash
python3 -c "from sar_parser import validate_file; print(validate_file('SARSupplement_NORMALIZED.xml').is_valid)"
```

## Security Notice

This document contains **confidential law enforcement sensitive information**. Unauthorized disclosure may be subject to civil and criminal penalties.

## Structure

The SAR XML document includes the following sections:
- Filing Information (metadata, submission IDs, dates)
- Filer Information (complainant details)
- Narrative Summary (case description)
- Subjects (entities and individuals involved)
- Transactions (wire transfers and financial movements)
- Properties (real estate involved)
- Indicators (red flags and suspicious activity patterns)
- Law Enforcement Contacts (FBI, FinCEN, IRS-CI)
- Exhibits (supporting documentation)
- Summary Statistics (transaction counts and totals)
