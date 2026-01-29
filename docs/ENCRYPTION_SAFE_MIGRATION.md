# Safe Migration: Non-Destructive Encryption Setup

## Overview

Safe migration enables git-crypt encryption **going forward** without changing git history. This is the recommended approach for most repositories.

**Time Required**: ⏱️ 5-10 minutes  
**Risk Level**: ✅ Low  
**Team Disruption**: ✅ None

---

## What This Does

✅ **Encrypts**:
- All new commits of matching files
- Existing matching files when re-committed
- Future sensitive data

❌ **Does NOT Encrypt**:
- Historical commits (old versions of files remain unencrypted)
- Files not yet re-committed after setup

---

## Prerequisites

### Install Git-Crypt

**macOS**:
```bash
brew install git-crypt
```

**Ubuntu/Debian**:
```bash
sudo apt-get install git-crypt
```

**Fedora/RHEL**:
```bash
sudo dnf install git-crypt
```

**Windows**:
Use WSL (Windows Subsystem for Linux) or download from [releases](https://github.com/AGWA/git-crypt/releases)

### Verify Installation

```bash
git-crypt --version
# Should show: git-crypt 0.6.0 or newer
```

---

## Step-by-Step Guide

### Step 1: Ensure Clean Working Directory

```bash
cd /path/to/stop-azs
git status
```

**Expected**: No uncommitted changes

**If you have changes**:
```bash
# Commit or stash them first
git add .
git commit -m "Save work before encryption setup"
# OR
git stash
```

---

### Step 2: Initialize Git-Crypt

```bash
git-crypt init
```

**Expected Output**:
```
Generating key...
```

✅ **Success**: No errors displayed  
⚠️ **Warning**: If you see "already initialized", git-crypt is already set up

---

### Step 3: Verify Configuration Files

The `.gitattributes` file should already exist in the repository. Verify it:

```bash
cat .gitattributes | head -20
```

**Expected**: You should see encryption patterns like:
```
docs/involved_parties.md filter=git-crypt diff=git-crypt
evidence/** filter=git-crypt diff=git-crypt
```

If `.gitattributes` is missing or incorrect, you may need to create or update it.

---

### Step 4: Check Encryption Status

```bash
git-crypt status
```

**Expected Output**:
```
not encrypted: .gitattributes
not encrypted: .gitignore
not encrypted: README.md
...
```

Files not yet committed will show `not encrypted` - this is normal!

---

### Step 5: Export Encryption Key

**Critical**: Save this key in a secure location!

```bash
# Export to a secure location
git-crypt export-key ~/git-crypt-stop-azs.key

# Verify the key was created
ls -lh ~/git-crypt-stop-azs.key
```

**Expected**: File size around 32-64 bytes

**Store the key**:
- ✅ Password manager (1Password, LastPass, Bitwarden)
- ✅ Encrypted USB drive
- ✅ Secure cloud storage (encrypted folder)
- ❌ **NEVER** commit the key to the repository
- ❌ **NEVER** send via plain email or Slack

**Backup locations**:
```bash
# Make multiple backups
cp ~/git-crypt-stop-azs.key ~/Dropbox/encrypted/git-crypt-stop-azs.key
# Add to password manager as file attachment
```

---

### Step 6: Commit Encryption Configuration

```bash
# Verify what's being committed
git status

# Expected: .gitattributes and possibly .gitignore
git add .gitattributes
git commit -m "feat: enable git-crypt encryption for sensitive files"
git push origin main
```

---

### Step 7: Verify Encryption Works

Create a test file to verify encryption:

```bash
# Create a test sensitive file
echo "SECRET TEST DATA - DO NOT COMMIT" > test.sensitive

# Add and commit it
git add test.sensitive
git commit -m "test: verify encryption"

# Check if it's encrypted
git-crypt status | grep test.sensitive
```

**Expected**: `encrypted: test.sensitive`

```bash
# Clean up test file
git rm test.sensitive
git commit -m "test: remove encryption test file"
```

---

### Step 8: Lock Repository to Verify

Test that encryption is working by locking and unlocking:

```bash
# Lock the repository (encrypts files in working directory)
git-crypt lock

# Try to read a sensitive file
cat test.sensitive 2>/dev/null || echo "File is encrypted!"

# Unlock repository
git-crypt unlock ~/git-crypt-stop-azs.key

# Now you can read files again
```

---

## Encrypting Existing Sensitive Files

If you already have sensitive files tracked in git that need encryption:

### Option A: Touch and Re-commit (Simple)

```bash
# Force git to re-encrypt files matching .gitattributes
git rm --cached -r .
git add .
git commit -m "chore: re-add files to trigger encryption"
git push
```

This re-adds all files, triggering encryption for files matching `.gitattributes` patterns.

### Option B: Selective Re-commit

```bash
# For specific files
git rm --cached docs/involved_parties.md
git add docs/involved_parties.md
git commit -m "chore: encrypt involved_parties.md"
git push
```

⚠️ **Important**: Old versions in git history remain unencrypted!

---

## Verification Checklist

After setup, verify everything works:

- [ ] `git-crypt status` shows no errors
- [ ] Files matching `.gitattributes` patterns show as `encrypted`
- [ ] Encryption key is backed up in secure location
- [ ] Test lock/unlock cycle works
- [ ] Changes are pushed to remote
- [ ] Team members can unlock with shared key

---

## Sharing Access with Team

### Export Key for Sharing

```bash
# Export the key
git-crypt export-key ~/git-crypt-stop-azs.key
```

### Share Securely

**Secure methods** (choose one):

1. **Password Manager Sharing**:
   - Upload key to 1Password/LastPass
   - Share vault with team member

2. **Encrypted Email**:
   ```bash
   # Using GPG
   gpg --encrypt --recipient teammate@example.com ~/git-crypt-stop-azs.key
   # Email the .gpg file
   ```

3. **Signal/WhatsApp**:
   - Send key file via encrypted messaging
   - Delete message after they save it

4. **In-Person**:
   - Transfer via USB drive
   - Screen share and guide them through upload to password manager

**DO NOT**:
- ❌ Send via plain email
- ❌ Send via Slack/Teams/Discord
- ❌ Commit to repository
- ❌ Post in issue tracker

### Team Member Setup

Share these instructions with team members:

```bash
# 1. Install git-crypt
brew install git-crypt  # or platform-specific command

# 2. Clone repository
git clone https://github.com/stopazus/stop-azs.git
cd stop-azs

# 3. Unlock with shared key
git-crypt unlock /path/to/git-crypt-stop-azs.key

# 4. Verify
git-crypt status
```

---

## Common Issues

### Issue: "Error: encryption not set up"

**Solution**:
```bash
# Re-initialize
git-crypt init
git add .gitattributes
git commit -m "feat: enable git-crypt"
```

### Issue: "File not encrypted after commit"

**Cause**: File doesn't match any pattern in `.gitattributes`

**Solution**:
```bash
# Check pattern
cat .gitattributes | grep "your-file"

# If missing, add pattern to .gitattributes
echo "your-file.txt filter=git-crypt diff=git-crypt" >> .gitattributes
git add .gitattributes your-file.txt
git commit -m "chore: add encryption for your-file.txt"
```

### Issue: "Already encrypted" when trying to view file

**Solution**:
```bash
# You need to unlock repository
git-crypt unlock /path/to/key
```

### Issue: Files show as encrypted locally but not on GitHub

**Solution**:
```bash
# Push changes
git push origin main

# Verify with remote check script
./scripts/verify-encryption-remote.sh
```

---

## What About Historical Sensitive Data?

Safe migration does NOT encrypt historical commits. If you have sensitive data in old commits:

**Options**:

1. **Accept the risk** (for private repos with access control)
2. **Rotate secrets** (change passwords/keys in old commits)
3. **Upgrade to clean migration** (see [ENCRYPTION_CLEAN_MIGRATION.md](ENCRYPTION_CLEAN_MIGRATION.md))

**For already-committed passwords**:
```bash
# 1. Rotate the password immediately (assume compromised)
# 2. Update systems with new password
# 3. Old password in history is now useless
```

---

## Maintenance

### Regular Tasks

**When team member leaves**:
```bash
# Option 1: Re-initialize with new key
git-crypt init -k new-key
# Export and share new key

# Option 2: Switch to GPG-based access control
# (see GIT_CRYPT_SETUP.md for GPG instructions)
```

**Verify encryption periodically**:
```bash
# Monthly check
git-crypt status
./scripts/check-encryption.sh
```

---

## Next Steps

✅ Encryption is now active for all new commits!

**Daily Usage**:
- Just work normally - encryption is automatic
- See [QUICK_START_ENCRYPTION.md](QUICK_START_ENCRYPTION.md) for common commands

**Advanced Topics**:
- GPG-based access control: [GIT_CRYPT_SETUP.md](GIT_CRYPT_SETUP.md)
- Detailed troubleshooting: [GIT_CRYPT_SETUP.md](GIT_CRYPT_SETUP.md)

**Automation**:
All these steps are automated in:
```bash
./scripts/setup-git-crypt.sh  # Choose option 1
```

---

## Summary

| Step | What Happened | Time |
|------|---------------|------|
| 1 | Clean working directory | 1 min |
| 2 | Initialize git-crypt | 1 min |
| 3 | Verify `.gitattributes` | 1 min |
| 4 | Export encryption key | 1 min |
| 5 | Commit configuration | 1 min |
| 6 | Test encryption | 2 min |
| 7 | Verify setup | 1 min |

**Total**: ~8 minutes

✅ **Result**: All future matching files are encrypted  
⚠️ **Remember**: Old commits remain unencrypted
