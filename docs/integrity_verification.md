SHA-256 INTEGRITY VERIFICATION SHEET
==========================================

File Name: Electronic_Dispatch_Packet_2025-10-11_vFinal.zip (reloaded from OneDrive form)
Recovered Archive Path: `C:\Users\stopazs\AppData\Local\Temp\9ce2b911-1eba-4359-a89a-66cff51d0dc3_Electronic_Dispatch_Packet_2025-10-11_vFinal.zip.dc3\Electronic_Dispatch_Packet_7065f609_2025-10-10_v9.zip`
Date Generated: October 12, 2025
Prepared by: N & S Holding LLC – AML Surveillance Unit
Contact: office@nsholding.us | +1 (786) 707-7111

Source Repository:
- SharePoint download (primary): <https://hsholdingllc-my.sharepoint.com/:x:/g/personal/sharon_peertel_us1/EdJxHwAcuLNNmsXyiZa44l8ByORYJsT0Fc2c8ra3sAGeag?e=nyhiho>
  - Hosted artifact: `Electronic_Dispatch_Packet_2025-10-11_vFinal.zip` (final signed packet bundled with supporting SAR documentation)
  - Retrieval metadata: Pulled October 12, 2025 at 14:22 UTC by AML Surveillance Unit personnel and hashed prior to archival
  - Access control: Restricted to N & S Holding LLC credentials; contact office@nsholding.us for compliance-driven guest access

SHA-256 Hash Value:
0f09f799f932eacece3ca23627fe1c32c4fe84658ad8f7396f3c90f7f9d52f78

Verification Method:
This checksum verifies the authenticity and integrity of the final electronic dispatch packet submitted to DOJ, FinCEN, IRS-CI, and FBI IC3.
To confirm authenticity, run either of the following commands:

    certutil -hashfile Electronic_Dispatch_Packet_2025-10-11_vFinal.zip SHA256
or
    sha256sum Electronic_Dispatch_Packet_2025-10-11_vFinal.zip

If the output matches the above hash value, the submission is confirmed as authentic and unaltered.

Digital Signature Placeholder:
/s/ Sharon Topaz
Manager & Authorized Representative
N & S Holding LLC

Suspicious Activity Report (SAR) Excerpt:
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
