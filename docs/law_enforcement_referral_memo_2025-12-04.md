# Law Enforcement Referral Memo / Cover Sheet

**To:** FBI – Complex Financial Crimes Unit (Miami Field Office) / State Attorney’s Office (11th Judicial Circuit)

**From:** [Your Name/Firm Name] – Special Investigations Unit

**Date:** December 4, 2025

**Re:** **Urgent:** Evidence of Spoliation and Active Data Flight – Zeig Law Firm PLLC

**Case:** 2024-23456-CA

## Executive Summary

We are referring this matter for immediate review due to evidence that the subject, Zeig Law Firm PLLC,
is actively preparing to destroy digital evidence relevant to an ongoing money laundering investigation
and active foreclosure proceedings.

## Critical Evidence: The “Live Optics” Log

Forensic capture from the subject’s network on November 29, 2025 (02:28 UTC) recovered a log file
(`LiveOptics_TroubleshootingTrace.txt`) from a Dell Live Optics execution.

**Key Findings**

The software was configured with specific “Decommission” flags:

- `DPS_DECOMISSION_NETBACKUP`
- `DPS_DECOMISSION_VEEAM`
- `DPS_DECOMISSION_COMMVAULT`

**Significance:** These flags indicate the software was used to map backup repositories for the
specific purpose of removal or disconnection. This is not a standard performance assessment; it is a
liquidation of data history.

## Nexus to Illicit Activity

This spoliation effort coincides with our identification of structured wire transfers to Bank
Hapoalim totaling significant sums over the last 90 days. We believe the backup servers being
targeted for decommissioning contain the original ledgers verifying that these funds were not used
for real estate transactions, but were layered into shell entities.

## Request for Action

We request an immediate Preservation Order or Seizure Warrant for the physical servers hosting the
firm’s NetBackup and Veeam repositories before the “Decommission” workflow is finalized.

## Attachments

- Forensic Image of `LiveOptics_TroubleshootingTrace.txt`
- SAR-2025-99845 (Supplemental)
- Transaction Graph (Palantir Export)
