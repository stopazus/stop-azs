# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 5.1.x   | :white_check_mark: |
| 5.0.x   | :x:                |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

## Reporting a Vulnerability

Use this section to tell people how to report a vulnerability.

Tell them where to go, how often they can expect to get an update on a
reported vulnerability, what to expect if the vulnerability is accepted or
declined, etc.

## Encrypted Files

This repository uses git-crypt to protect sensitive investigation data.

### Reporting Issues with Encrypted Files

If you believe:
- A file should be encrypted but isn't
- The encryption key has been compromised
- You've found encrypted data in plaintext in git history

**DO NOT** create a public issue. Instead:

1. Email stopazus directly at GitHub (@stopazus)
2. Use GitHub's private vulnerability reporting feature
3. Open a security advisory on GitHub

### Key Management

- Encryption keys are NEVER committed to the repository
- Keys are backed up in secure, encrypted locations
- Keys are rotated when team members leave or if compromised
