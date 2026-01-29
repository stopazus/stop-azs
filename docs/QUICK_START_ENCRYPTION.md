# Quick Start: Git-Crypt Encryption

## First Time Setup (5 minutes)

### Install git-crypt
```bash
# macOS
brew install git-crypt

# Ubuntu
sudo apt-get install git-crypt
```

### For Repository Owner
```bash
# 1. Initialize (one-time only)
git-crypt init

# 2. Export key to safe location
git-crypt export-key ~/Secure/stop-azs-key

# 3. Back up the key (password manager, encrypted USB, etc.)

# 4. Verify
git-crypt status
```

### For Collaborators
```bash
# 1. Get key from @stopazus securely

# 2. Clone repository
git clone https://github.com/stopazus/stop-azs.git
cd stop-azs

# 3. Unlock
git-crypt unlock /path/to/key

# 4. Verify
cat docs/involved_parties.md
# Should show readable text
```

## Daily Usage

Work normally - encryption is automatic:

```bash
# Edit files
vim docs/involved_parties.md

# Commit
git add docs/involved_parties.md
git commit -m "Update investigation details"

# Push (file is encrypted automatically)
git push
```

## Verify Encryption

```bash
# Check status
./scripts/check-encryption.sh

# Verify remote
./scripts/verify-encryption-remote.sh
```

That's it! 🎉
