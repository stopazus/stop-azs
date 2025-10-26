# Electronic Dispatch Packet Integrity Verification

## Summary
- **File Name:** `Electronic_Dispatch_Packet_2025-10-11_vFinal.zip`
- **Date Generated:** October 12, 2025
- **Prepared By:** N & S Holding LLC – AML Surveillance Unit
- **Contact:** [office@nsholding.us](mailto:office@nsholding.us) | +1 (786) 707-7111

## SHA-256 Checksum
```
0f09f799f932eacece3ca23627fe1c32c4fe84658ad8f7396f3c90f7f9d52f78
```

To confirm authenticity, run either command below and compare the output with the checksum above:

```powershell
certutil -hashfile Electronic_Dispatch_Packet_2025-10-11_vFinal.zip SHA256
```

```bash
sha256sum Electronic_Dispatch_Packet_2025-10-11_vFinal.zip
```

Matching results confirm the dispatch packet submitted to DOJ, FinCEN, IRS-CI, and FBI IC3 is authentic and unaltered.

## Digital Signature Placeholder
```
/s/ Sharon Topaz
Manager & Authorized Representative
N & S Holding LLC
```

## Suspicious Activity Report (SAR)
The SAR excerpt provided by the AML Surveillance Unit is captured below for internal reference.

```xml
<SAR xmlns="http://www.fincen.gov/base" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.5">
  <FilingInformation>
    <FilingType>Initial</FilingType>
    <FilingDate>2025-09-11</FilingDate>
    <AmendmentType>None</AmendmentType>
    <PriorDocumentControlNumber/>
    <ContactOffice>N &amp; S Holding LLC - AML Surveillance Unit</ContactOffice>
    <ContactPhone>786-707-7111</ContactPhone>
    <ContactEmail>office@nsholding.us</ContactEmail>
  </FilingInformation>
  <FilerInformation>
    <FilerName>N &amp; S Holding LLC</FilerName>
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
    <Narrative>
      IC3 Submission ID 7065f60922b948a59af3a8654edb16dd. Funds originated from Zeig IOTA Escrow, routed through pass-through accounts #2304977980 and #2000043165557, and dispersed to YBH Holdings LLC, Eisenstein Buyers, and layered offshore accounts. Dollar amounts and UETR identifiers pending subpoena from Banesco USA.
    </Narrative>
  </SuspiciousActivity>
  <Attachments>
    <Attachment>
      <FileName>Consolidated_SAR_Report_IC3_7065f60922b948a59af3a8654edb16dd.pdf</FileName>
      <Description>Annex supplement with transaction tables, flowchart, compliance recommendations, and embedded subpoena request.</Description>
    </Attachment>
  </Attachments>
</SAR>
```

## Supplemental References
- Flight itinerary screenshot documenting Miami ➔ Tel Aviv departure on **Saturday, July 05** via EL AL flight LY22 (non-stop, 11h 55m).
- Hebrew-language worksheet illustrating fraction representations and exercises (page labeled "שברים במילים ובמספרים" / "Fractions in words and numbers").
- Transaction flow network diagram highlighting suspected movement of funds among Wells Fargo, SunTrust, CMB accounts, YBH Holdings, Eisenstein Buyers, EU Shell Co., and related entities.

These artifacts should be stored in the secure evidence archive alongside the electronic dispatch packet.
