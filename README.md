# stop-azs
This repository documents key allegations and participants in the alleged diversion of escrow funds
from the City National Bank trust account controlled by Justin E. Zeig. See [analysis.md](analysis.md)
for detailed background on the trust account activity, summaries of the shell entities involved,
captured case metadata, identified red flags, an expanded forensic ledger exhibit (as of 24 August
2025), and a concluding synthesis that ties the observed pass-through behavior to the ongoing
recovery and enforcement efforts.

## Windows NAS Bootstrap

The [windows-nas-bootstrap](windows-nas-bootstrap/) directory contains a Windows automation bundle that:
- Installs essential applications via winget (Python 3.12, Git, rclone, VS Code, 7-Zip, VLC, WinSCP, PuTTY)
- G:\My Drive\AICD
- Performs optional network speed tests

See [windows-nas-bootstrap/README.md](windows-nas-bootstrap/README.md) for usage instructions.

## External Research Resources

Investigators occasionally stage AI-assisted narratives or drafting notes outside the repository before
promoting them into `analysis.md`. A living index of those destinations now lives in
[`docs/external_resources.md`](docs/external_resources.md). Each entry records the location, primary
custodian, and handling expectations so contributors know how to access the Gemini workspace and any future
off-repo staging areas without breaking the evidence trail.

## Request Flow

The end-to-end path for a client submission—from the public API endpoint through validation and into the
database—is captured in [`docs/request_flow.md`](docs/request_flow.md), including a Mermaid diagram that
highlights each security, validation, and persistence hop.

## 🔒 File Encryption with Git-Crypt

This repository uses [git-crypt](https://github.com/AGWA/git-crypt) to encrypt sensitive investigation files.

### What's Encrypted

Files are **automatically encrypted** when committed and **transparently decrypted** for authorized users:

- 📄 **`docs/involved_parties.md`** - Investigation participant details
- 📁 **`evidence/`, `case_files/`, `investigation/`** - Case data directories
- 🔐 **`secrets/`, `credentials/`** - Authentication data
- 🔑 **SSL certificates** (`.pem`, `.key`, `.crt`)
- ⚙️ **Production configs** (`.env.production`, `.env.staging`)
- 📋 **Marked files** (`*.sensitive`, `*.confidential`, `*.private`)
- 📊 **SAR exports** (`data/sar/*.xml`, `exports/*.sar`)

### Quick Start

**For New Users:**

1. **Install git-crypt:**
   ```bash
   # macOS
   brew install git-crypt
   
   # Ubuntu/Debian
   sudo apt-get install git-crypt
   ```

2. **Run setup wizard:**
   ```bash
   ./scripts/setup-git-crypt.sh
   ```

3. **Follow the prompts** - the wizard handles everything!

**For Existing Collaborators:**

```bash
# Get encryption key from @stopazus (securely!)
git-crypt unlock /path/to/key
```

### Documentation

- 🎯 **Decision Guide** - [Which migration path?](docs/ENCRYPTION_DECISION_GUIDE.md)
- 📘 **Safe Migration** - [5-minute setup](docs/ENCRYPTION_SAFE_MIGRATION.md)
- 🔥 **Clean Migration** - [Advanced, rewrites history](docs/ENCRYPTION_CLEAN_MIGRATION.md)
- 📖 **Full Guide** - [Complete documentation](docs/GIT_CRYPT_SETUP.md)
- ⚡ **Quick Reference** - [Common commands](docs/QUICK_START_ENCRYPTION.md)

### Verification

Check encryption status anytime:

```bash
# Quick check
git-crypt status

# Detailed verification
./scripts/check-encryption.sh

# Verify GitHub encryption
./scripts/verify-encryption-remote.sh
```

### Daily Usage

Once unlocked, work normally - encryption is automatic:

```bash
# Edit sensitive files
vim docs/involved_parties.md

# Commit and push as usual
git add docs/involved_parties.md
git commit -m "Update investigation details"
git push

# ✨ File is automatically encrypted before push!
```

### Security Notes

⚠️ **What Git-Crypt Protects:**
- ✅ File contents in current and future commits
- ✅ Data at rest on GitHub
- ✅ Prevents unauthorized access

⚠️ **What It Does NOT Protect:**
- ❌ Git history before encryption was enabled
- ❌ Commit messages (never put sensitive info here!)
- ❌ File names and directory structure

🔑 **Key Management:**
- Never commit the encryption key to the repository
- Back up keys in password manager or encrypted vault
- Share keys only via secure channels (Signal, encrypted email)
- Rotate keys when team members leave

## Testing

The project currently has no automated test suite. A `pytest` run (August 2025) reports zero
collected tests, confirming that no executable checks are defined yet.
