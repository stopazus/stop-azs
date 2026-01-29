<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  
  <xsl:template match="/">
    <html>
      <head>
        <title>SAR Supplement Report - <xsl:value-of select="/SAR/FilingInformation/IC3SubmissionID"/></title>
        <style type="text/css">
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
            color: #333;
          }
          .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
          }
          h1 {
            color: #1a4d7a;
            border-bottom: 3px solid #1a4d7a;
            padding-bottom: 10px;
          }
          h2 {
            color: #2563a8;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 5px;
            margin-top: 30px;
          }
          h3 {
            color: #4a90d9;
            margin-top: 20px;
          }
          .metadata {
            background-color: #f0f8ff;
            padding: 15px;
            border-left: 4px solid #1a4d7a;
            margin: 20px 0;
          }
          .metadata-item {
            margin: 5px 0;
          }
          .metadata-label {
            font-weight: bold;
            color: #1a4d7a;
            display: inline-block;
            width: 150px;
          }
          .narrative {
            background-color: #fffef0;
            padding: 15px;
            border-left: 4px solid #d4a017;
            margin: 20px 0;
            line-height: 1.6;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          }
          th {
            background-color: #1a4d7a;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
          }
          td {
            padding: 10px;
            border-bottom: 1px solid #e0e0e0;
          }
          tr:nth-child(even) {
            background-color: #f9f9f9;
          }
          tr:hover {
            background-color: #f0f8ff;
          }
          .amount {
            font-weight: bold;
            color: #2e7d32;
          }
          .status-executed {
            color: #2e7d32;
            font-weight: bold;
          }
          .status-pending {
            color: #f57c00;
            font-weight: bold;
          }
          .indicator {
            background-color: #fff3e0;
            padding: 8px;
            margin: 5px 0;
            border-left: 3px solid #f57c00;
          }
          .contact-card {
            background-color: #e8f5e9;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #2e7d32;
          }
          .contact-agency {
            font-weight: bold;
            color: #1b5e20;
            font-size: 1.1em;
          }
          .summary-box {
            background-color: #e3f2fd;
            padding: 20px;
            margin: 20px 0;
            border: 2px solid #1a4d7a;
            border-radius: 5px;
          }
          .summary-item {
            margin: 10px 0;
            font-size: 1.1em;
          }
          .summary-label {
            font-weight: bold;
            color: #1a4d7a;
            display: inline-block;
            width: 200px;
          }
          ul.exhibit-list {
            list-style-type: none;
            padding-left: 0;
          }
          ul.exhibit-list li {
            background-color: #f5f5f5;
            padding: 8px;
            margin: 5px 0;
            border-left: 3px solid #757575;
          }
          .warning {
            background-color: #ffebee;
            padding: 15px;
            border-left: 4px solid #c62828;
            margin: 20px 0;
            font-weight: bold;
            color: #c62828;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Suspicious Activity Report - Supplement</h1>
          
          <div class="warning">
            CONFIDENTIAL - LAW ENFORCEMENT SENSITIVE
          </div>
          
          <div class="metadata">
            <div class="metadata-item">
              <span class="metadata-label">Filing Type:</span>
              <xsl:value-of select="/SAR/FilingInformation/FilingType"/>
            </div>
            <div class="metadata-item">
              <span class="metadata-label">Filing Date:</span>
              <xsl:value-of select="/SAR/FilingInformation/FilingDate"/>
            </div>
            <div class="metadata-item">
              <span class="metadata-label">Generated:</span>
              <xsl:value-of select="/SAR/FilingInformation/GeneratedAt"/>
              (<xsl:value-of select="/SAR/FilingInformation/Timezone"/>)
            </div>
            <div class="metadata-item">
              <span class="metadata-label">IC3 Submission ID:</span>
              <xsl:value-of select="/SAR/FilingInformation/IC3SubmissionID"/>
            </div>
          </div>
          
          <h2>Filer Information</h2>
          <div class="metadata">
            <div class="metadata-item">
              <span class="metadata-label">Filer Name:</span>
              <xsl:value-of select="/SAR/FilerInformation/FilerName"/>
            </div>
            <div class="metadata-item">
              <span class="metadata-label">Address:</span>
              <xsl:value-of select="/SAR/FilerInformation/FilerAddress/AddressLine1"/>,
              <xsl:value-of select="/SAR/FilerInformation/FilerAddress/City"/>,
              <xsl:value-of select="/SAR/FilerInformation/FilerAddress/State"/>
            </div>
            <div class="metadata-item">
              <span class="metadata-label">Matter:</span>
              <xsl:value-of select="/SAR/FilerInformation/Matter"/>
            </div>
            <div class="metadata-item">
              <span class="metadata-label">Incident Date:</span>
              <xsl:value-of select="/SAR/FilerInformation/IncidentDate"/>
            </div>
            <div class="metadata-item">
              <span class="metadata-label">Wire Reference:</span>
              <xsl:value-of select="/SAR/FilerInformation/WireReference"/>
            </div>
          </div>
          
          <h2>Narrative Summary</h2>
          <div class="narrative">
            <xsl:value-of select="/SAR/NarrativeSummary"/>
          </div>
          
          <h2>Subjects</h2>
          <table>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Role</th>
              <th>Jurisdiction</th>
              <th>Details</th>
            </tr>
            <xsl:for-each select="/SAR/Subjects/Subject">
              <tr>
                <td><xsl:value-of select="Name"/></td>
                <td><xsl:value-of select="EntityType"/></td>
                <td><xsl:value-of select="Role"/></td>
                <td><xsl:value-of select="Jurisdiction"/></td>
                <td>
                  <xsl:if test="Status">
                    Status: <xsl:value-of select="Status"/><br/>
                  </xsl:if>
                  <xsl:if test="DoingBusinessIn">
                    DBA: <xsl:value-of select="DoingBusinessIn"/><br/>
                  </xsl:if>
                  <xsl:if test="TrustNumber">
                    Trust #: <xsl:value-of select="TrustNumber"/><br/>
                  </xsl:if>
                  <xsl:if test="RecordedProperty">
                    Property: <xsl:value-of select="RecordedProperty"/>
                  </xsl:if>
                </td>
              </tr>
            </xsl:for-each>
          </table>
          
          <h2>Transactions</h2>
          <table>
            <tr>
              <th>Date/Time</th>
              <th>Amount</th>
              <th>From</th>
              <th>To</th>
              <th>Reference</th>
              <th>Status</th>
            </tr>
            <xsl:for-each select="/SAR/Transactions/Transaction">
              <tr>
                <td><xsl:value-of select="Date"/></td>
                <td class="amount">
                  <xsl:value-of select="Amount/@currency"/>
                  <xsl:text> </xsl:text>
                  <xsl:value-of select="format-number(Amount, '#,##0.00')"/>
                </td>
                <td>
                  <xsl:value-of select="OriginatingAccount/BankName"/><br/>
                  <xsl:if test="OriginatingAccount/AccountNumber">
                    Acct: <xsl:value-of select="OriginatingAccount/AccountNumber"/><br/>
                  </xsl:if>
                  <xsl:value-of select="OriginatingAccount/AccountHolder"/>
                </td>
                <td>
                  <xsl:value-of select="ReceivingAccount/BankName"/><br/>
                  <xsl:if test="ReceivingAccount/ABARouting">
                    ABA: <xsl:value-of select="ReceivingAccount/ABARouting"/><br/>
                  </xsl:if>
                  <xsl:if test="ReceivingAccount/AccountNumber">
                    Acct: <xsl:value-of select="ReceivingAccount/AccountNumber"/><br/>
                  </xsl:if>
                  <xsl:value-of select="ReceivingAccount/AccountHolder"/>
                </td>
                <td>
                  <xsl:value-of select="Reference"/>
                  <xsl:if test="PropertyAddress">
                    <br/><strong>Property:</strong> <xsl:value-of select="PropertyAddress"/>
                  </xsl:if>
                  <xsl:if test="Notes">
                    <br/><em><xsl:value-of select="Notes"/></em>
                  </xsl:if>
                </td>
                <td>
                  <xsl:attribute name="class">
                    <xsl:choose>
                      <xsl:when test="Status = 'Executed'">status-executed</xsl:when>
                      <xsl:otherwise>status-pending</xsl:otherwise>
                    </xsl:choose>
                  </xsl:attribute>
                  <xsl:value-of select="Status"/>
                </td>
              </tr>
            </xsl:for-each>
          </table>
          
          <h2>Properties</h2>
          <table>
            <tr>
              <th>Address</th>
              <th>Status</th>
              <th>Owner/Details</th>
              <th>Purchase Price</th>
              <th>Notes</th>
            </tr>
            <xsl:for-each select="/SAR/Properties/Property">
              <tr>
                <td><xsl:value-of select="Address"/></td>
                <td><xsl:value-of select="Status"/></td>
                <td>
                  <xsl:if test="RecordedOwner">
                    Owner: <xsl:value-of select="RecordedOwner"/><br/>
                  </xsl:if>
                  <xsl:if test="AllegedControlEntity">
                    Control: <xsl:value-of select="AllegedControlEntity"/>
                  </xsl:if>
                </td>
                <td>
                  <xsl:if test="PurchasePrice">
                    <span class="amount">
                      <xsl:value-of select="PurchasePrice/@currency"/>
                      <xsl:text> </xsl:text>
                      <xsl:value-of select="format-number(PurchasePrice, '#,##0.00')"/>
                    </span>
                  </xsl:if>
                </td>
                <td><xsl:value-of select="Notes"/></td>
              </tr>
            </xsl:for-each>
          </table>
          
          <h2>Red Flags and Indicators</h2>
          <xsl:for-each select="/SAR/Indicators/Indicator">
            <div class="indicator">
              <xsl:value-of select="."/>
            </div>
          </xsl:for-each>
          
          <h2>Law Enforcement Contacts</h2>
          <xsl:for-each select="/SAR/LawEnforcementContacts/Contact">
            <div class="contact-card">
              <div class="contact-agency"><xsl:value-of select="Agency"/></div>
              <div><strong>Program:</strong> <xsl:value-of select="Program"/></div>
              <div><strong>Reference:</strong> <xsl:value-of select="Reference"/></div>
              <div><strong>Requested Action:</strong> <xsl:value-of select="RequestedAction"/></div>
            </div>
          </xsl:for-each>
          
          <h2>Exhibits</h2>
          <ul class="exhibit-list">
            <xsl:for-each select="/SAR/Exhibits/Exhibit">
              <li><xsl:value-of select="."/></li>
            </xsl:for-each>
          </ul>
          
          <h2>Summary Statistics</h2>
          <div class="summary-box">
            <div class="summary-item">
              <span class="summary-label">Total Transactions:</span>
              <xsl:value-of select="/SAR/Summary/TotalTransactions"/>
            </div>
            <div class="summary-item">
              <span class="summary-label">Total Amount (USD):</span>
              <span class="amount">$<xsl:value-of select="format-number(/SAR/Summary/TotalAmountUSD, '#,##0.00')"/></span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Earliest Transaction:</span>
              <xsl:value-of select="/SAR/Summary/EarliestTransaction"/>
            </div>
            <div class="summary-item">
              <span class="summary-label">Latest Transaction:</span>
              <xsl:value-of select="/SAR/Summary/LatestTransaction"/>
            </div>
          </div>
          
          <div class="warning" style="margin-top: 40px;">
            This document contains confidential law enforcement sensitive information. Unauthorized disclosure may be subject to civil and criminal penalties.
          </div>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
