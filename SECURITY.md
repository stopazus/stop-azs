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
- The affected product and exact version(s).
- A short summary of the vulnerability and its impact.
- Steps to reproduce (proof-of-concept) or a minimal test case.
- Any relevant logs, stack traces, or sample exploit code.
- Your contact details and whether you want a public credit.

Do NOT post the vulnerability publicly (including repository issues or Discussions) until disclosure is coordinated.

## Encrypted Communication

If you prefer encrypted communication, include a PGP public key or similar in your initial email and we will use it for sensitive information. You can paste the key block inline or provide a URL to a keyserver or key file.

## What to expect after you report

- Acknowledgement: We will acknowledge receipt within 3 business days.
- Triage: We will assess severity and begin work to produce a fix.
- Updates: We will provide status updates at reasonable intervals (typically within 7 days while the issue is being worked on).
- Fix &amp; disclosure: We will coordinate a disclosure timeline with the reporter. Our default disclosure window is 90 days from initial report, but this may be shortened or extended depending on the specifics and severity of the issue.
- CVE: We will request a CVE for issues that meet CVE criteria.
- Credit: We will credit the reporter unless they request anonymity.

If a reported issue poses an immediate, widespread threat to safety or critical infrastructure, we may shorten the disclosure timeline and will communicate this to the reporter.

## Reporting Third-Party Dependencies

If you find a vulnerability in a third-party dependency used by this project, please report it to the dependency's maintainer first where possible, and notify us so we can coordinate a fix and release.

## Safe Harbor / Legal

We will not threaten legal action against security researchers who follow the guidelines in this policy and make a good-faith effort to avoid privacy violations and destruction of data. Do not access or exfiltrate user data when testing; keep reports limited to demonstration of the vulnerability.

## Changes to this Policy

This policy may be updated from time to time. The latest version of this file in this repository is the authoritative policy.

## Contact

Email: security@stopazus.dev
GitHub: Open a repository security advisory (preferred)
