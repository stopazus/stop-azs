# Security Policy

## Supported Versions

This project follows a predictable supported-versions policy for security fixes. If a version series is marked as supported, critical and high-severity security fixes will be backported and released for that series.

| Version | Supported |
| ------- | --------- |
| 5.1.x   | :white_check_mark: |
| 5.0.x   | :x: |
| 4.0.x   | :white_check_mark: |
| &lt; 4.0   | :x: |

If your version is no longer supported, we strongly recommend upgrading to a supported release.

## Reporting a Vulnerability

We appreciate responsible disclosures. To report a security vulnerability, please follow one of the options below:

1. Preferred: Open a GitHub Security Advisory for this repository (recommended). See: https://docs.github.com/en/code-security/security-advisories/about-security-advisories

2. Email: security@stopazus.dev

When reporting, please include as much of the following as possible:
- A clear description of the affected product and version.
- A short summary of the vulnerability and potential impact.
- Steps to reproduce (proof of concept) or a small test case.
- Any relevant logs, stack traces, or poc code.
- Your contact information (so we can follow up).

Do NOT post the vulnerability publicly (including issues or Discussions) until it has been fixed and coordinated disclosure has taken place.

## What to expect

- Acknowledgement: We will acknowledge receipt within 3 business days.
- Triage: We will assess severity and begin work to produce a fix.
- Updates: We will provide status updates at reasonable intervals (typically within 7 days while the issue is being worked on).
- Fix and disclosure: We will coordinate a disclosure timeline with the reporter. Our default disclosure window is 90 days from initial report, but this may be shortened or extended depending on the specifics and severity.
- CVE: We will request a CVE for issues that meet CVE criteria and will credit the reporter unless they request anonymity.

If the vulnerability poses an immediate threat to safety or widely deployed infrastructure, we may shorten the disclosure timeline and will communicate this to the reporter.

## Supported Communication and Encryption

If you prefer encrypted communications, provide a PGP key in your initial email and we will use it for sensitive information.

## Reporting Third-Party Dependencies

If you discover a vulnerability in a third-party dependency used by this project, please report it to the dependency's maintainer first where possible and notify us so we can coordinate a fix and release.

## Security Policy Changes

We may update this policy from time to time. The latest version of this file in the repository is the authoritative policy.
