# Git-Crypt Setup and Usage Guide

Complete documentation for git-crypt encryption in the stop-azs repository.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Initial Setup](#initial-setup)
4. [Daily Usage](#daily-usage)
5. [Key Management](#key-management)
6. [Collaboration](#collaboration)
7. [Advanced Topics](#advanced-topics)
8. [Troubleshooting](#troubleshooting)
9. [Security Best Practices](#security-best-practices)

---

## Overview

### What is Git-Crypt?

Git-crypt enables transparent encryption and decryption of files in a git repository. Files are:
- **Encrypted** when committed to git
- **Decrypted** automatically for authorized users
- **Binary blobs** for unauthorized users

### What Files Are Encrypted?

See `.gitattributes` for the complete list. Key patterns:

- **Investigation docs**: `docs/involved_parties.md`
- **Evidence directories**: `evidence/**`, `case_files/**`, `investigation/**`
- **Credentials**: `secrets/**`, `credentials/**`, `.env.production`
- **SSL certificates**: `*.pem`, `*.key`, `*.crt`
- **Sensitive markers**: `*.sensitive`, `*.confidential`, `*.private`
- **SAR exports**: `data/sar/*.xml`, `sar_exports/**`

### How It Works

```
┌─────────────────┐
│  Working Tree   │ ← Files are decrypted (readable)
│   (unlocked)    │
└────────┬────────┘
         │ git add / commit
         ↓
┌─────────────────┐
│  Git Repository │ ← Files are encrypted (binary)
│   (.git/...)    │
└────────┬────────┘
         │ git push
         ↓
┌─────────────────┐
│  GitHub Remote  │ ← Files are encrypted (secure)
│                 │
└─────────────────┘
```

### Security Model

✅ **Protects against**:
- Unauthorized access to repository
- Accidental public disclosure
- Data breaches of hosting platform

❌ **Does NOT protect against**:
- Historical commits before encryption was enabled
- Commit messages (never put secrets here!)
- File names and directory structure
- Users with the decryption key

---

## Installation

### macOS

```bash
# Using Homebrew
brew install git-crypt

# Verify installation
git-crypt --version
```

### Ubuntu/Debian

```bash
# Using apt
sudo apt-get update
sudo apt-get install git-crypt

# Verify installation
git-crypt --version
```

### Fedora/RHEL/CentOS

```bash
# Using dnf
sudo dnf install git-crypt

# Verify installation
git-crypt --version
```

### Windows

**Option 1: WSL (Recommended)**
```powershell
# Install WSL if not already installed
wsl --install

# Inside WSL
sudo apt-get update
sudo apt-get install git-crypt
```

**Option 2: Native Windows**
- Download from [GitHub releases](https://github.com/AGWA/git-crypt/releases)
- Extract to `C:\Program Files\git-crypt\`
- Add to PATH

### Verify Installation

```bash
git-crypt --version
# Expected: git-crypt 0.6.0 or newer
```

---

## Initial Setup

### For Repository Administrators

If you're setting up git-crypt for the first time:

#### Option 1: Interactive Wizard (Recommended)

```bash
./scripts/setup-git-crypt.sh
```

Follow the prompts to choose migration path.

#### Option 2: Manual Setup

See detailed guides:
- [Safe Migration](ENCRYPTION_SAFE_MIGRATION.md) - Non-destructive (recommended)
- [Clean Migration](ENCRYPTION_CLEAN_MIGRATION.md) - Rewrites history (advanced)

### For Collaborators

If git-crypt is already set up:

1. **Install git-crypt** (see [Installation](#installation))

2. **Clone repository**:
   ```bash
   git clone https://github.com/stopazus/stop-azs.git
   cd stop-azs
   ```

3. **Get encryption key** from repository admin (@stopazus)
   - Via password manager share
   - Via encrypted email
   - Via Signal/WhatsApp
   - **NEVER** via plain email or Slack

4. **Unlock repository**:
   ```bash
   git-crypt unlock /path/to/git-crypt-stop-azs.key
   ```

5. **Verify**:
   ```bash
   git-crypt status
   cat docs/involved_parties.md  # Should be readable
   ```

---

## Daily Usage

Once unlocked, git-crypt is transparent - work normally!

### Regular Workflow

```bash
# Edit sensitive files normally
vim docs/involved_parties.md

# Add and commit as usual
git add docs/involved_parties.md
git commit -m "Update investigation details"

# Push - encryption happens automatically!
git push origin main
```

### Check Encryption Status

```bash
# Quick status
git-crypt status

# Detailed check
git-crypt status -e  # Show encrypted files only
git-crypt status -u  # Show unencrypted files only

# Use helper script
./scripts/check-encryption.sh
```

### Lock Repository

Lock repository (encrypt working tree files):

```bash
# Lock repository
git-crypt lock

# Files are now encrypted in working directory
cat docs/involved_parties.md
# Shows binary gibberish

# Unlock to work again
git-crypt unlock
```

**Use cases for locking**:
- Stepping away from computer
- Handing off laptop
- Testing encryption

### Create New Sensitive Files

Files matching `.gitattributes` patterns are automatically encrypted:

```bash
# Create file with sensitive extension
echo "Confidential data" > analysis.confidential

# Commit normally
git add analysis.confidential
git commit -m "Add confidential analysis"
git push

# Verify encryption
git-crypt status | grep analysis.confidential
# Output: encrypted: analysis.confidential
```

### Add New Encryption Patterns

To encrypt new file types:

1. Edit `.gitattributes`:
   ```bash
   echo "*.new-extension filter=git-crypt diff=git-crypt" >> .gitattributes
   ```

2. Commit pattern:
   ```bash
   git add .gitattributes
   git commit -m "Add encryption for .new-extension files"
   git push
   ```

3. Re-encrypt existing files with new extension:
   ```bash
   git rm --cached file.new-extension
   git add file.new-extension
   git commit -m "Re-encrypt file.new-extension"
   git push
   ```

---

## Key Management

### Export Encryption Key

```bash
# Export symmetric key
git-crypt export-key ~/git-crypt-stop-azs.key

# Verify export
ls -lh ~/git-crypt-stop-azs.key
```

### Store Key Securely

**Recommended storage**:
- ✅ Password manager (1Password, LastPass, Bitwarden)
- ✅ Encrypted USB drive
- ✅ Encrypted cloud storage (Dropbox encrypted folder)
- ✅ Hardware security key (Yubikey)

**DO NOT store**:
- ❌ In repository
- ❌ In plaintext on disk
- ❌ In email
- ❌ In Slack/Teams

### Backup Key

Create multiple backups:

```bash
# Local backup
cp ~/git-crypt-stop-azs.key ~/Dropbox/encrypted/

# Password manager
# Upload as secure note or file attachment in 1Password

# Secure USB
cp ~/git-crypt-stop-azs.key /media/encrypted-usb/
```

### Rotate Key

When team member leaves or key is compromised:

```bash
# 1. Initialize new key
git-crypt init

# 2. Re-encrypt repository
git rm --cached -r .
git add .
git commit -m "Rotate git-crypt key"

# 3. Export new key
git-crypt export-key ~/git-crypt-stop-azs-NEW.key

# 4. Push changes
git push origin main

# 5. Share new key with team (securely)
# 6. Team re-unlocks with new key
```

---

## Collaboration

### Add Collaborator (Symmetric Key)

**Administrator**:
1. Export key:
   ```bash
   git-crypt export-key ~/key-for-alice.key
   ```

2. Share securely:
   - Password manager sharing
   - Encrypted email (GPG)
   - Signal/WhatsApp
   - In-person USB transfer

**Collaborator**:
1. Clone repository:
   ```bash
   git clone https://github.com/stopazus/stop-azs.git
   cd stop-azs
   ```

2. Unlock:
   ```bash
   git-crypt unlock ~/key-for-alice.key
   ```

3. Verify:
   ```bash
   git-crypt status
   ```

### Add Collaborator (GPG Key)

More secure, no key sharing needed:

**Collaborator** (do first):
1. Generate GPG key if needed:
   ```bash
   gpg --gen-key
   # Follow prompts
   ```

2. Export public key:
   ```bash
   gpg --export --armor alice@example.com > alice.asc
   ```

3. Share `alice.asc` with administrator (can be public)

**Administrator**:
1. Import collaborator's public key:
   ```bash
   gpg --import alice.asc
   ```

2. Add GPG user to git-crypt:
   ```bash
   git-crypt add-gpg-user alice@example.com
   ```

3. Commit and push:
   ```bash
   git commit -m "Add Alice to git-crypt"
   git push origin main
   ```

**Collaborator**:
1. Pull changes:
   ```bash
   git pull origin main
   ```

2. Unlock (automatically with GPG):
   ```bash
   git-crypt unlock
   # Uses your GPG key automatically
   ```

### Remove Collaborator Access

**Symmetric key**: Rotate key (see [Rotate Key](#rotate-key))

**GPG key**:
```bash
# Remove GPG user
git-crypt rm-gpg-user alice@example.com

# Commit changes
git commit -m "Remove Alice from git-crypt"
git push origin main

# Alice can no longer decrypt new commits
# (But can still decrypt old commits she already has)
```

**Complete removal** (even from old commits): Requires clean migration (history rewrite).

---

## Advanced Topics

### Using Git-Crypt with CI/CD

**GitHub Actions**:

1. Export key:
   ```bash
   git-crypt export-key ~/git-crypt.key
   ```

2. Base64 encode:
   ```bash
   base64 ~/git-crypt.key > git-crypt.key.base64
   ```

3. Add as GitHub secret:
   - GitHub → Settings → Secrets → New repository secret
   - Name: `GIT_CRYPT_KEY`
   - Value: Contents of `git-crypt.key.base64`

4. Use in workflow:
   ```yaml
   - name: Unlock git-crypt
     run: |
       echo "${{ secrets.GIT_CRYPT_KEY }}" | base64 -d > /tmp/git-crypt.key
       git-crypt unlock /tmp/git-crypt.key
       rm /tmp/git-crypt.key
   ```

### Exclude Files from Encryption

Add to `.gitattributes`:

```gitattributes
# This file should NOT be encrypted
docs/public-doc.md !filter !diff
```

The `!filter` negates encryption even if it matches another pattern.

### Check Individual File Encryption

```bash
# Check if specific file is encrypted
git-crypt status | grep docs/involved_parties.md

# Check attribute
git check-attr filter docs/involved_parties.md
# Output: docs/involved_parties.md: filter: git-crypt
```

### View Encrypted Content Without Decrypting

```bash
# View encrypted binary content
git show main:docs/involved_parties.md | xxd | head

# Will show encrypted binary data
```

### Convert Existing Repository

See migration guides:
- [Safe Migration](ENCRYPTION_SAFE_MIGRATION.md)
- [Clean Migration](ENCRYPTION_CLEAN_MIGRATION.md)

---

## Troubleshooting

### Files Not Encrypting

**Problem**: Committed file not encrypted

**Diagnosis**:
```bash
git-crypt status | grep your-file
git check-attr filter your-file
```

**Solutions**:

1. **File doesn't match pattern**:
   ```bash
   # Add pattern to .gitattributes
   echo "your-file filter=git-crypt diff=git-crypt" >> .gitattributes
   git add .gitattributes your-file
   git commit -m "Add encryption for your-file"
   ```

2. **File committed before git-crypt initialized**:
   ```bash
   # Re-commit to trigger encryption
   git rm --cached your-file
   git add your-file
   git commit -m "Re-encrypt your-file"
   ```

3. **Pattern syntax error**:
   ```bash
   # Check .gitattributes syntax
   cat .gitattributes
   # Fix any errors in patterns
   ```

### Can't Unlock Repository

**Problem**: `git-crypt unlock` fails

**Solutions**:

1. **Wrong key file**:
   ```bash
   # Verify key file
   ls -lh /path/to/key
   # Should be 32-64 bytes
   
   # Try different key file
   git-crypt unlock /correct/path/to/key
   ```

2. **Repository not initialized**:
   ```bash
   # Check if git-crypt is set up
   git-crypt status
   # If error, repository needs initialization
   ```

3. **Corrupted key**:
   ```bash
   # Get fresh key copy from administrator
   # Re-unlock with fresh key
   ```

### Files Show as Binary in Diff

**Problem**: `git diff` shows binary for text files

**Solution**:

```bash
# Ensure you're unlocked
git-crypt unlock

# Set diff attribute in .gitattributes
# Should already have: diff=git-crypt

# Verify
git check-attr diff docs/involved_parties.md
```

### Accidentally Committed Unencrypted Sensitive File

**Problem**: Pushed sensitive file before git-crypt was set up

**Solutions**:

1. **Immediate**: Rotate secrets (assume compromised)

2. **Remove from history** (if recent):
   ```bash
   # For last commit
   git reset --soft HEAD^
   
   # Add encryption pattern
   echo "sensitive-file filter=git-crypt diff=git-crypt" >> .gitattributes
   git add .gitattributes sensitive-file
   git commit -m "Add encryption for sensitive-file"
   
   # Force-push (if not shared with team yet)
   git push origin main --force
   ```

3. **Remove from all history**:
   Use [Clean Migration](ENCRYPTION_CLEAN_MIGRATION.md) guide

### Repository Already Initialized

**Problem**: `git-crypt init` says "already initialized"

**Solutions**:

1. **Already set up - just unlock**:
   ```bash
   git-crypt unlock /path/to/key
   ```

2. **Need to re-initialize**:
   ```bash
   # Remove git-crypt metadata
   rm -rf .git/git-crypt
   
   # Re-initialize
   git-crypt init
   ```

### Files Encrypted Locally But Not on GitHub

**Problem**: Files show encrypted locally but readable on GitHub

**Solutions**:

1. **Not pushed**:
   ```bash
   git push origin main
   ```

2. **Encryption not triggered on GitHub**:
   ```bash
   # Verify remote file
   ./scripts/verify-encryption-remote.sh
   
   # If not encrypted, re-commit
   git rm --cached file
   git add file
   git commit -m "Re-trigger encryption"
   git push origin main
   ```

### Getting "Smudge Error" on Git Pull

**Problem**: Error when pulling: "git-crypt smudge error"

**Solution**:

```bash
# Repository is locked, need to unlock
git-crypt unlock /path/to/key

# Then pull again
git pull origin main
```

---

## Security Best Practices

### ✅ DO

- Use git-crypt for files with sensitive data
- Store encryption key in password manager
- Create multiple key backups
- Rotate keys when team members leave
- Use GPG keys for better access control
- Verify encryption status regularly
- Lock repository when stepping away
- Share keys only via secure channels
- Document who has access to keys

### ❌ DON'T

- Don't commit encryption key to repository
- Don't put secrets in commit messages
- Don't share keys via email or Slack
- Don't assume file names are hidden (they're not!)
- Don't rely on git-crypt for compliance (consult legal)
- Don't forget to back up encryption key
- Don't give key to people who don't need access
- Don't use git-crypt for large binary files (poor performance)

### Key Rotation Schedule

Rotate encryption keys:
- **Immediately**: When team member leaves with access
- **Immediately**: When key is suspected compromised
- **Quarterly**: Proactive security practice
- **Annually**: Minimum for compliance

### Audit Trail

Track encryption operations:

```bash
# Who initialized git-crypt
git log --all --grep="git-crypt" --oneline

# When keys were rotated
git log --all -S "git-crypt" --oneline

# Files added to encryption
git log --all -- .gitattributes
```

---

## Quick Reference

### Common Commands

```bash
# Check status
git-crypt status

# Lock repository
git-crypt lock

# Unlock repository
git-crypt unlock /path/to/key

# Export key
git-crypt export-key /path/to/key

# Add GPG user
git-crypt add-gpg-user user@example.com

# Initialize new repository
git-crypt init
```

### Helper Scripts

```bash
# Interactive setup wizard
./scripts/setup-git-crypt.sh

# Check encryption status
./scripts/check-encryption.sh

# Verify remote encryption
./scripts/verify-encryption-remote.sh

# Share access with collaborator
./scripts/share-access.sh
```

---

## Additional Resources

### Documentation

- [Decision Guide](ENCRYPTION_DECISION_GUIDE.md) - Choose migration path
- [Safe Migration](ENCRYPTION_SAFE_MIGRATION.md) - Non-destructive setup
- [Clean Migration](ENCRYPTION_CLEAN_MIGRATION.md) - History rewrite
- [Quick Start](QUICK_START_ENCRYPTION.md) - Common commands

### External Links

- [Git-Crypt GitHub](https://github.com/AGWA/git-crypt)
- [Git-Crypt Man Page](https://www.agwa.name/projects/git-crypt/)
- [Git Attributes Documentation](https://git-scm.com/docs/gitattributes)

---

## Support

For issues with git-crypt in this repository:

1. Check [Troubleshooting](#troubleshooting) section
2. Review helper scripts output: `./scripts/check-encryption.sh`
3. Contact repository administrator (@stopazus)
4. For git-crypt bugs: [GitHub Issues](https://github.com/AGWA/git-crypt/issues)

---

**Last Updated**: 2026-01-29  
**Git-Crypt Version**: 0.6.0+  
**Repository**: stopazus/stop-azs
