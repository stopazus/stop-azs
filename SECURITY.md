# Security Policy

## Supported Versions

This repository uses git-crypt for file encryption. All versions are actively maintained.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| All branches | :white_check_mark: |

## Encrypted Files

This repository uses git-crypt to encrypt sensitive investigation data.

### Encryption Coverage

Sensitive files are automatically encrypted using AES-256:
- Investigation participant details
- Case evidence and documentation
- Credentials and API keys
- SSL certificates and private keys
- Production configuration files

See `.gitattributes` for complete list of encrypted patterns.

### Reporting Encryption Issues

If you discover:
- A file that should be encrypted but isn't
- Sensitive data in plaintext in git history
- A compromised encryption key
- Unauthorized access to encrypted files

**DO NOT** create a public issue or commit. Instead:

1. **Email @stopazus directly** (see contact info in `docs/involved_parties.md`)
2. Use **GitHub's private vulnerability reporting**
3. Contact via **encrypted channel** (Signal, PGP email)

### Key Security

- 🔑 Encryption keys are **NEVER** committed to this repository
- 🔒 Keys are stored in encrypted password managers
- 🔄 Keys are rotated when:
  - Team members leave the project
  - Keys are suspected to be compromised
  - Annually as a security best practice
- 📤 Keys are shared only via:
  - Encrypted email (PGP)
  - Secure messaging (Signal, WhatsApp)
  - Password manager sharing features
  - **NEVER** via Slack, Teams, or plain email

### Encryption Audit Trail

All encryption operations are logged:
- When git-crypt was initialized
- Who has access (via GPG keys or shared key)
- When keys were rotated
- When access was revoked

Contact repository admins for audit logs.

## Reporting a Vulnerability

If you discover a security vulnerability in this repository:

1. **For encrypted data issues**: See "Reporting Encryption Issues" above
2. **For other security issues**: 
   - Use GitHub's private vulnerability reporting
   - Or email repository maintainer directly
   - Provide details: affected files, severity, reproduction steps

You can expect:
- Acknowledgment within 48 hours
- Initial assessment within 1 week
- Regular updates on remediation progress
- Public disclosure only after fix is implemented
