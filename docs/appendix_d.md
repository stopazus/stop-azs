# Appendix D: Inferred Ownership & Control Structure – 3049 Perriwinkle Circle

This appendix illustrates the inferred ownership and control structure for the property at 3049 Perriwinkle Circle. Based on deed metadata, escrow flow analysis, and offshore layering patterns, this structure highlights how shell entities and nominee holdings are used to obscure beneficial ownership and facilitate suspected laundering.

## Transaction & Wire Integration

- **TX1**: $5,000 → Shell Entity (purpose unclear, probable layering or consulting fee masking).
- **TX2**: $206,693.68 → Shannon G. Tomchin (also the deed grantor, indicating self-dealing).
- Wire memo anomalies such as `ZLG-XXXX-XX` suggest spoofed internal code formats inconsistent with legitimate bank records.
- Structuring characteristics include nominal deed consideration ($10), rerouting of funds through an escrow intermediary, and immediate cycling back to the grantor.

## Executive Findings

- Zeig Law Firm PLLC acted as escrow controller and document preparer.
- Tomchin appears both as grantor and escrow proceeds recipient, a red flag of circular laundering.
- Offshore entities including YBH Holdings 2948 LLC, Bitton Nominee Holdings, and Ben-Hamo Trust (Cayman) appear as inferred beneficiaries.
- This layered structure matches IRS/FinCEN typologies for real estate laundering.

## Suspicious Activity Report Snapshot

```
<SAR xmlns="http://www.fincen.gov/base" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.5">
<FilingInformation>
<FilingType>Initial</FilingType>
<FilingDate>2025-09-11</FilingDate>
<AmendmentType>None</AmendmentType>
<PriorDocumentControlNumber/>
<ContactOffice>N & S Holding LLC - AML Surveillance Unit</ContactOffice>
<ContactPhone>786-707-7111</ContactPhone>
<ContactEmail>office@nsholding.us</ContactEmail>
</FilingInformation>
<FilerInformation>
<FilerName>N & S Holding LLC</FilerName>
<FilerEIN/>
<FilerAddress>
<AddressLine1>2640 Hollywood Blvd</AddressLine1>
<City>Hollywood</City>
<State>FL</State>
<ZIP>33020</ZIP>
<Country>US</Country>
</FilerAddress>
<SAM>
<UEI>QD5XW4H6MNX8</UEI>
<CAGE>87AY0</CAGE>
</SAM>
</FilerInformation>
<Subjects>
<Subject>
<EntityType>Business</EntityType>
<Name>YBH Holdings LLC</Name>
<Account>
<AccountNumber/>
<FinancialInstitution/>
</Account>
</Subject>
<Subject>
<EntityType>Business</EntityType>
<Name>Eisenstein Buyers</Name>
<Account>
<AccountNumber/>
<FinancialInstitution/>
</Account>
</Subject>
<Subject>
<EntityType>Business</EntityType>
<Name>Zeig IOTA Escrow</Name>
<Account>
<AccountNumber/>
<FinancialInstitution/>
</Account>
</Subject>
</Subjects>
<Transactions>
<Transaction>
<Date>2023-02-09</Date>
<Amount currency="USD">PENDING</Amount>
<OriginatingAccount>
<Name>Zeig IOTA Escrow</Name>
</OriginatingAccount>
<PassThroughAccounts>
<Account>#2304977980</Account>
<Account>#2000043165557</Account>
</PassThroughAccounts>
<Beneficiaries>
<Beneficiary>YBH Holdings LLC</Beneficiary>
<Beneficiary>Eisenstein Buyers</Beneficiary>
<Beneficiary>Layered Offshore Accounts</Beneficiary>
</Beneficiaries>
<UETR>PENDING</UETR>
<Notes>Routing inconsistent with escrow instructions; suspected layering/structuring.</Notes>
</Transaction>
</Transactions>
<SuspiciousActivity>
<Activities>
<Activity>Wire fraud - escrow diversion</Activity>
<Activity>Money laundering - layering</Activity>
<Activity>Structuring</Activity>
</Activities>
<Locations>
<KnownAddress>1040 Hsia Bitoon</KnownAddress>
</Locations>
<Narrative> IC3 Submission ID 7065f60922b948a59af3a8654edb16dd. Funds originated from Zeig IOTA Escrow, routed through pass-through accounts #2304977980 and #2000043165557, and dispersed to YBH Holdings LLC, Eisenstein Buyers, and layered offshore accounts. Dollar amounts and UETR identifiers pending subpoena from Banesco USA. </Narrative>
</SuspiciousActivity>
<Attachments>
<Attachment>
<FileName>Consolidated_SAR_Report_IC3_7065f60922b948a59af3a8654edb16dd.pdf</FileName>
<Description>Annex supplement with transaction tables, flowchart, compliance recommendations, and embedded subpoena request.</Description>
</Attachment>
</Attachments>
</SAR>
```

## Ownership & Control Diagram

```mermaid
graph LR
    A[3049 Perriwinkle Circle]
    B[Shannon G. Tomchin]
    C[Zeig Law Firm PLLC]
    D[YBH Holdings 2948 LLC]
    E[Bitton Nominee Holdings]
    F[Ben-Hamo Trust (Cayman)]
    G[Zeig IOTA Escrow]
    H[Eisenstein Buyers]

    A -- Deed grantor --> B
    B -- Escrow instructions --> C
    C -- Controls --> G
    G -- TX1 $5,000 --> D
    G -- TX2 $206,693.68 --> B
    D -- Ownership link --> E
    E -- Beneficiary --> F
    G -- Pass-through accounts --> H
    H -- Offshore layering --> F
```

*Figure D-1. Layered ownership structure showing connections among the property, escrow agent, and offshore beneficiaries.*
