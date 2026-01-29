# Git-Crypt Setup Guide

## What is Git-Crypt?

Git-crypt enables transparent encryption of files in a git repository. Selected files are encrypted when pushed to GitHub and automatically decrypted when checked out by authorized users.

**Files encrypted in this repository:**
- `docs/involved_parties.md` - Investigation participant details
- `evidence/`, `case_files/`, `investigation/` - Case data directories
- `*.sensitive`, `*.confidential` - Explicitly marked files
- `secrets/`, `credentials/` - Authentication data
- SSL certificates and private keys
- Production/staging environment files

## Installation

### macOS
```bash
brew install git-crypt
```

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install git-crypt
```

### Windows
1. Download from [git-crypt releases](https://github.com/AGWA/git-crypt/releases)
2. Extract to a directory in your PATH
3. Or use WSL and follow Linux instructions

### Verify Installation
```bash
git-crypt --version
# Should output: git-crypt 0.7.0 or higher
```

## First-Time Repository Setup

### For Repository Owner (@stopazus)

**1. Initialize git-crypt (one-time setup):**
```bash
cd stop-azs
git-crypt init
```

**2. Export the encryption key:**
```bash
# Export to a secure location OUTSIDE the repository
git-crypt export-key ../stop-azs-git-crypt-key

# CRITICAL: Back up this key file securely!
# Store in password manager, encrypted backup, or secure vault
```

**3. Verify encryption is working:**
```bash
# Check which files are encrypted
git-crypt status

# Files marked with "encrypted" should include:
# - docs/involved_parties.md
# - Any files in evidence/, case_files/, etc.
```

**4. Lock the repository to test:**
```bash
# Lock (files become encrypted blobs)
git-crypt lock

# Check that involved_parties.md is now binary/encrypted
file docs/involved_parties.md
# Should show: "data" or "GPG encrypted"

# Unlock to continue working
git-crypt unlock ../stop-azs-git-crypt-key
```

### For Collaborators

**Option A: Using Shared Key (Simple)**

1. Obtain the encryption key from @stopazus (via secure channel - NEVER email or Slack)
2. Clone the repository:
   ```bash
   git clone https://github.com/stopazus/stop-azs.git
   cd stop-azs
   ```
3. Unlock the repository:
   ```bash
   git-crypt unlock /path/to/stop-azs-git-crypt-key
   ```
4. Verify access:
   ```bash
   cat docs/involved_parties.md
   # Should show readable text, not binary data
   ```

**Option B: Using GPG (Recommended for Teams)**

1. Generate GPG key if you don't have one:
   ```bash
   gpg --full-generate-key
   # Choose: RSA and RSA, 4096 bits, key doesn't expire
   ```

2. Share your GPG key ID with @stopazus:
   ```bash
   gpg --list-keys
   # Find your key ID (long hex string)
   ```

3. Repository owner adds you:
   ```bash
   git-crypt add-gpg-user YOUR_GPG_KEY_ID
   git push
   ```

4. Clone and unlock automatically:
   ```bash
   git clone https://github.com/stopazus/stop-azs.git
   cd stop-azs
   # Files decrypt automatically if you're authorized
   ```

## Daily Usage

Once unlocked, git-crypt works transparently:

```bash
# Edit sensitive files normally
echo "Sensitive info" > evidence/case001.txt

# Commit and push as usual
git add evidence/case001.txt
git commit -m "Add case evidence"
git push

# File is automatically encrypted before push
# No special commands needed!
```

## Verification Commands

### Check Encryption Status
```bash
# See which files are encrypted
git-crypt status

# Example output:
# encrypted: docs/involved_parties.md
# encrypted: evidence/document.pdf
# not encrypted: README.md
# not encrypted: sar_parser/validator.py
```

### Verify Files Are Encrypted in Remote Repository
```bash
# Clone to a new directory WITHOUT unlocking
git clone https://github.com/stopazus/stop-azs.git test-clone
cd test-clone

# Try to read encrypted file
cat docs/involved_parties.md
# Should show binary garbage or "GITCRYPT" header

# Clean up
cd ..
rm -rf test-clone
```

## Key Management

### Backing Up the Encryption Key

**CRITICAL: Without the key, encrypted data is irrecoverable!**

```bash
# Create encrypted backup of the key
gpg --symmetric --cipher-algo AES256 stop-azs-git-crypt-key
# Creates: stop-azs-git-crypt-key.gpg

# Store backups in:
# 1. Password manager (1Password, Bitwarden, etc.)
# 2. Encrypted USB drive in secure location
# 3. Encrypted cloud storage (NOT the same GitHub account)
```

### Rotating the Encryption Key

If the key is compromised:

```bash
# 1. Generate new key
git-crypt init --force

# 2. Export new key
git-crypt export-key ../stop-azs-git-crypt-key-new

# 3. Re-encrypt all files
git-crypt lock
git-crypt unlock ../stop-azs-git-crypt-key-new

# 4. Commit and force-push (DESTRUCTIVE - coordinate with team!)
git add -A
git commit -m "Rotate git-crypt key"
git push --force

# 5. Notify all collaborators to re-unlock with new key
```

## Troubleshooting

### Files Not Encrypting

```bash
# Check .gitattributes is committed
git ls-files .gitattributes

# Re-encrypt files
git-crypt lock
git-crypt unlock /path/to/key
git add -A
git commit -m "Re-encrypt files"
```

### "git-crypt: command not found"

Install git-crypt (see Installation section above)

### Files Showing as Binary in Diffs

This is normal for encrypted files. To see actual content:
```bash
git-crypt unlock /path/to/key
```

### Accidentally Committed Unencrypted Sensitive File

```bash
# If NOT yet pushed:
git reset --soft HEAD~1
# Set up .gitattributes pattern
git add .gitattributes
git-crypt lock && git-crypt unlock /path/to/key
git add -A
git commit -m "Encrypt sensitive file"

# If ALREADY pushed:
# Contact @stopazus - may need to rewrite history
```

## Security Notes

### What Git-Crypt Protects

✅ File contents in current and future commits  
✅ Files matching .gitattributes patterns  
✅ Data at rest on GitHub servers  

### What Git-Crypt Does NOT Protect

❌ Old commits before git-crypt was enabled  
❌ Commit messages (never put sensitive info here!)  
❌ File names and directory structure  
❌ Repository metadata  
❌ Access by authorized users (they can decrypt everything)  

### Best Practices

1. **Never commit the encryption key** to the repository
2. **Always verify** files are encrypted before pushing sensitive data
3. **Use GPG mode** for teams (better access control)
4. **Back up the key** in multiple secure locations
5. **Rotate keys** if compromised or when team members leave
6. **Don't reuse keys** across multiple repositories

## Quick Reference

```bash
# Status
git-crypt status                    # Check encryption status

# Lock/Unlock
git-crypt lock                      # Encrypt all files (working dir)
git-crypt unlock /path/to/key       # Decrypt all files

# Key Management
git-crypt export-key path/to/key    # Export symmetric key
git-crypt add-gpg-user USER_ID      # Add GPG user

# Verification
file docs/involved_parties.md       # Check if file is binary
git-crypt status -e                 # Show only encrypted files
```

## Support

Questions? Contact @stopazus or see:
- [Git-Crypt GitHub](https://github.com/AGWA/git-crypt)
- [Git-Crypt Documentation](https://github.com/AGWA/git-crypt/blob/master/README.md)
