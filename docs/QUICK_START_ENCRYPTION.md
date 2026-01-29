# Quick Start: Git-Crypt Encryption

Fast reference for common git-crypt operations.

---

## Installation

```bash
# macOS
brew install git-crypt

# Ubuntu/Debian
sudo apt-get install git-crypt

# Verify
git-crypt --version
```

---

## First Time Setup

### Option 1: Automated (Recommended)

```bash
./scripts/setup-git-crypt.sh
# Choose option 1 (Safe) or 2 (Clean)
```

### Option 2: Manual

```bash
# Initialize
git-crypt init

# Verify .gitattributes exists
cat .gitattributes

# Export key
git-crypt export-key ~/git-crypt-stop-azs.key

# Commit configuration
git add .gitattributes
git commit -m "feat: enable git-crypt encryption"
git push origin main
```

---

## Daily Operations

### Check Status

```bash
# Quick status
git-crypt status

# Detailed check
./scripts/check-encryption.sh

# Check specific file
git-crypt status | grep filename
```

### Lock/Unlock

```bash
# Lock (encrypt working directory)
git-crypt lock

# Unlock (decrypt working directory)
git-crypt unlock /path/to/key

# Unlock with GPG (if configured)
git-crypt unlock
```

### Work with Encrypted Files

```bash
# Edit normally (when unlocked)
vim docs/involved_parties.md

# Commit normally - encryption is automatic
git add docs/involved_parties.md
git commit -m "Update investigation details"
git push
```

---

## Key Management

### Export Key

```bash
# Export symmetric key
git-crypt export-key ~/git-crypt-stop-azs.key

# Backup to secure location
cp ~/git-crypt-stop-azs.key ~/Dropbox/encrypted/
```

### Share Key Securely

✅ **Safe Methods**:
- Password manager sharing (1Password, LastPass)
- Encrypted email (GPG): `gpg --encrypt --recipient user@example.com key`
- Signal/WhatsApp
- In-person USB transfer

❌ **NEVER**:
- Plain email
- Slack/Teams
- Commit to repository
- Public channels

---

## Collaboration

### New Team Member

**Admin**:
```bash
# Export key for sharing
git-crypt export-key ~/key-for-alice.key
# Share securely
```

**Team Member**:
```bash
# Clone repository
git clone https://github.com/stopazus/stop-azs.git
cd stop-azs

# Unlock with shared key
git-crypt unlock ~/key-for-alice.key

# Verify
git-crypt status
cat docs/involved_parties.md  # Should be readable
```

---

## Adding New Encrypted Files

### Files Matching Existing Patterns

Files automatically encrypted if they match `.gitattributes` patterns:

```bash
# These are auto-encrypted:
touch evidence/report.pdf       # evidence/** pattern
touch secrets/api.key            # secrets/** pattern
touch analysis.sensitive         # *.sensitive pattern

# Commit normally
git add .
git commit -m "Add encrypted files"
git push
```

### New File Patterns

```bash
# 1. Add pattern to .gitattributes
echo "*.secret filter=git-crypt diff=git-crypt" >> .gitattributes

# 2. Commit pattern
git add .gitattributes
git commit -m "Add encryption for .secret files"

# 3. Create and commit file
echo "data" > file.secret
git add file.secret
git commit -m "Add secret file"
git push

# 4. Verify
git-crypt status | grep file.secret
```

---

## Troubleshooting

### File Not Encrypting

```bash
# Check if pattern matches
git check-attr filter yourfile
# Should show: yourfile: filter: git-crypt

# If not matching, add to .gitattributes
echo "yourfile filter=git-crypt diff=git-crypt" >> .gitattributes
git add .gitattributes yourfile
git commit -m "Encrypt yourfile"
git push
```

### Can't Unlock

```bash
# Verify key file
ls -lh /path/to/key  # Should be ~32-64 bytes

# Try unlock with correct key
git-crypt unlock /correct/path/to/key

# If still fails, get fresh key from admin
```

### File Already Encrypted Error

```bash
# Repository is locked, unlock first
git-crypt unlock /path/to/key
```

### Accidentally Committed Unencrypted

```bash
# 1. Add encryption pattern
echo "sensitive-file filter=git-crypt diff=git-crypt" >> .gitattributes

# 2. Re-commit file
git add .gitattributes sensitive-file
git commit -m "Encrypt sensitive-file"
git push

# 3. IMPORTANT: Rotate any secrets in the file
# (They may be compromised from the unencrypted commit)
```

---

## Verification

### Verify Local Encryption

```bash
# Check status
git-crypt status

# Lock and check files are binary
git-crypt lock
cat docs/involved_parties.md  # Should show binary gibberish

# Unlock again
git-crypt unlock /path/to/key
```

### Verify Remote Encryption

```bash
# Use helper script
./scripts/verify-encryption-remote.sh

# Or manually check GitHub
# Browse to encrypted file on GitHub
# Should show binary/encrypted content
```

---

## Encrypted Files in This Repo

Current encryption patterns (see `.gitattributes`):

| Pattern | Example | Description |
|---------|---------|-------------|
| `docs/involved_parties.md` | (exact file) | Investigation docs |
| `evidence/**` | `evidence/case1.pdf` | Evidence files |
| `case_files/**` | `case_files/data.xlsx` | Case data |
| `secrets/**` | `secrets/api.key` | Secrets directory |
| `*.pem`, `*.key` | `server.pem` | SSL certificates |
| `*.sensitive` | `report.sensitive` | Marked files |
| `.env.production` | (exact file) | Production config |
| `data/sar/*.xml` | `data/sar/export.xml` | SAR exports |

---

## Common Workflows

### Rotating Encryption Key

```bash
# 1. Re-initialize git-crypt
git-crypt init

# 2. Re-encrypt all files
git rm --cached -r .
git add .
git commit -m "Rotate git-crypt key"

# 3. Export new key
git-crypt export-key ~/git-crypt-NEW.key

# 4. Push changes
git push origin main

# 5. Share new key with team
# 6. Team re-unlocks with new key
```

### Testing Encryption Setup

```bash
# 1. Create test file
echo "test data" > test.sensitive

# 2. Commit
git add test.sensitive
git commit -m "test: encryption"

# 3. Verify encrypted
git-crypt status | grep test.sensitive
# Should show: encrypted: test.sensitive

# 4. Cleanup
git rm test.sensitive
git commit -m "test: cleanup"
```

### Moving Between Machines

```bash
# Machine 1: Export key
git-crypt export-key ~/key.key
# Transfer key to Machine 2 securely

# Machine 2: Clone and unlock
git clone https://github.com/stopazus/stop-azs.git
cd stop-azs
git-crypt unlock ~/key.key
```

---

## Security Checklist

Before committing sensitive data:

- [ ] Git-crypt is initialized (`git-crypt status` works)
- [ ] File matches encryption pattern in `.gitattributes`
- [ ] Verified encryption: `git-crypt status | grep yourfile`
- [ ] Encryption key is backed up securely
- [ ] Team members who need access have the key
- [ ] No secrets in commit messages
- [ ] Tested lock/unlock cycle works

---

## Emergency Procedures

### Leaked Encryption Key

```bash
# 1. Immediately rotate key
git-crypt init  # New key

# 2. Re-encrypt repository
git rm --cached -r .
git add .
git commit -m "Emergency key rotation"
git push origin main

# 3. Export new key
git-crypt export-key ~/new-key.key

# 4. Notify team to use new key
# 5. Revoke old key from all storage
```

### Committed Unencrypted Secrets

```bash
# 1. IMMEDIATELY rotate all exposed secrets
# (Assume they are compromised)

# 2. Add encryption pattern
echo "leaked-file filter=git-crypt diff=git-crypt" >> .gitattributes

# 3. Re-commit
git add .gitattributes leaked-file
git commit -m "Encrypt leaked-file"
git push

# 4. Consider clean migration to remove from history
# See: docs/ENCRYPTION_CLEAN_MIGRATION.md
```

---

## Helper Scripts

Quick access to automation:

```bash
# Interactive setup wizard
./scripts/setup-git-crypt.sh

# Safe migration (non-destructive)
./scripts/safe-migration.sh

# Clean migration (history rewrite)
./scripts/clean-migration.sh

# Check encryption status
./scripts/check-encryption.sh

# Verify GitHub encryption
./scripts/verify-encryption-remote.sh

# Share access with collaborator
./scripts/share-access.sh
```

---

## Getting Help

**Documentation**:
- Full guide: [GIT_CRYPT_SETUP.md](GIT_CRYPT_SETUP.md)
- Decision guide: [ENCRYPTION_DECISION_GUIDE.md](ENCRYPTION_DECISION_GUIDE.md)
- Safe migration: [ENCRYPTION_SAFE_MIGRATION.md](ENCRYPTION_SAFE_MIGRATION.md)
- Clean migration: [ENCRYPTION_CLEAN_MIGRATION.md](ENCRYPTION_CLEAN_MIGRATION.md)

**Support**:
- Check troubleshooting section in [GIT_CRYPT_SETUP.md](GIT_CRYPT_SETUP.md)
- Run `./scripts/check-encryption.sh` for diagnostics
- Contact repository admin (@stopazus)

---

## Key Reminders

> 🔑 **Backup your encryption key** - no key = no access  
> 🔒 **Lock before stepping away** - `git-crypt lock`  
> ✅ **Verify encryption** - `git-crypt status`  
> 🚫 **Never commit the key** - store in password manager  
> 🔄 **Rotate keys** - when team members leave  

---

**Version**: 2026-01-29  
**Repository**: stopazus/stop-azs  
**For detailed docs**: See [GIT_CRYPT_SETUP.md](GIT_CRYPT_SETUP.md)
