# Clean Migration: History Rewrite with Full Encryption

## ⚠️ WARNING: Advanced Procedure

This guide rewrites git history to encrypt sensitive files in **all commits**, past and present.

**Time Required**: ⏱️ 30-45 minutes  
**Risk Level**: 🔥 **High**  
**Team Disruption**: 🔥 **Severe** (force-push, re-clone required)

---

## ⚠️ Before You Start

### Read This Carefully

This procedure will:
- 🔥 **Rewrite entire git history** (all commit SHAs change)
- 🔥 **Require force-push** to remote repository
- 🔥 **Break all open pull requests** (must be recreated)
- 🔥 **Force team to delete and re-clone** repository
- 🔥 **Cannot be easily undone**

### When to Use Clean Migration

✅ **Use clean migration if**:
- Passwords/API keys exist in git history
- PII/sensitive legal data is in history
- Repository is or was public
- Compliance requires complete encryption

❌ **Do NOT use if**:
- Team is actively working (coordinate first!)
- You're uncomfortable with force-push
- You want to test first (use safe migration)

---

## Prerequisites

### Required Tools

```bash
# Git-crypt
brew install git-crypt  # macOS
sudo apt-get install git-crypt  # Ubuntu/Debian

# git-filter-repo (for history rewriting)
brew install git-filter-repo  # macOS
pip3 install git-filter-repo  # Ubuntu/Debian

# Verify installations
git-crypt --version
git-filter-repo --version
```

### Team Coordination

**48 hours before**:
- [ ] Notify all team members
- [ ] Schedule migration window
- [ ] Request everyone commits pending work
- [ ] Pause all CI/CD pipelines
- [ ] Document all open pull requests

**During migration**:
- [ ] Block all commits (GitHub branch protection)
- [ ] Disable CI/CD
- [ ] Communicate status updates

**After migration**:
- [ ] Team deletes local clones
- [ ] Team re-clones repository
- [ ] Recreate pull requests
- [ ] Re-enable CI/CD

---

## Pre-Migration Checklist

### 1. Identify Sensitive Files

```bash
# List all files in history
git log --pretty=format: --name-only --diff-filter=A | sort -u > all-files.txt

# Review for sensitive data
grep -E "\.(pem|key|env)" all-files.txt
grep -E "secret|password|credential" all-files.txt
```

Review and note which files need encryption.

### 2. Verify .gitattributes Patterns

```bash
cat .gitattributes
```

Ensure all sensitive files match a pattern. If not, update `.gitattributes` before proceeding.

### 3. Create Backup

```bash
# Create backup branch
git branch backup-pre-encryption-$(date +%Y%m%d)

# Push backup to remote
git push origin backup-pre-encryption-$(date +%Y%m%d)

# Tag current state
git tag pre-encryption-$(date +%Y%m%d)
git push origin pre-encryption-$(date +%Y%m%d)
```

### 4. Inform Team

Send notification:
```
Subject: REQUIRED ACTION - Git Repository Encryption Migration

The stop-azs repository will undergo encryption migration:

DATE: [Schedule date/time]
DURATION: ~45 minutes
IMPACT: Force-push, must re-clone repository

REQUIRED ACTIONS:
1. Commit and push all work by [deadline]
2. Note all open pull requests
3. After migration, DELETE local clone
4. Re-clone: git clone https://github.com/stopazus/stop-azs.git
5. Unlock: git-crypt unlock [key file]

NEW ENCRYPTION KEY will be shared after migration.
```

---

## Migration Procedure

### Step 1: Clean Working Directory

```bash
cd /path/to/stop-azs

# Ensure clean state
git status
# Should show: "nothing to commit, working tree clean"

# If not clean
git add .
git commit -m "chore: save work before encryption migration"
git push origin main
```

### Step 2: Initialize Git-Crypt

```bash
# Initialize git-crypt
git-crypt init

# Verify initialization
git-crypt status
```

**Expected**: Command succeeds, shows encryption status

### Step 3: Commit .gitattributes

```bash
# Add encryption configuration
git add .gitattributes
git commit -m "feat: add git-crypt encryption configuration"

# DO NOT PUSH YET - we'll rewrite history first
```

### Step 4: Prepare Filter-Repo Script

Create a script to re-encrypt historical files:

```bash
cat > /tmp/reencrypt.sh << 'EOF'
#!/bin/bash
# This script runs during filter-repo to trigger encryption

# Re-add files to trigger git-crypt filters
git rm --cached -r . || true
git add .

# Ensure .gitattributes is processed
git add .gitattributes
EOF

chmod +x /tmp/reencrypt.sh
```

### Step 5: Rewrite History with git-filter-repo

⚠️ **Point of No Return**: After this step, you must complete the migration.

```bash
# Create a clone for the rewrite (safer than working in-place)
cd /tmp
git clone /path/to/stop-azs stop-azs-rewrite
cd stop-azs-rewrite

# Initialize git-crypt in the clone
git-crypt init

# Ensure .gitattributes is present
git checkout main
git add .gitattributes

# Run filter-repo to rewrite history
git filter-repo --force --commit-callback '
import subprocess
subprocess.run(["git", "rm", "--cached", "-r", "."], check=False)
subprocess.run(["git", "add", "."], check=True)
'

# Alternative simpler approach using --path-glob
# This forces all files to be re-processed, triggering git-crypt
git filter-repo --force --invert-paths --path-glob '**/.git*'
git filter-repo --force --prune-empty always
```

**Expected**: Process completes without errors (may take 5-20 minutes)

### Alternative Approach: Simpler History Rewrite

If the above fails, use this proven approach:

```bash
cd /path/to/stop-azs

# Remove all cached files and re-add (triggers git-crypt)
git rm --cached -r .
git add .
git commit -m "feat: re-encrypt repository with git-crypt"

# For older commits, use filter-branch (older but more reliable)
git filter-branch --index-filter '
  git rm --cached -r --ignore-unmatch .
  git add .
' --prune-empty --tag-name-filter cat -- --all

# Clean up refs
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d
```

### Step 6: Verify Encryption

```bash
# Check encryption status
git-crypt status

# Verify files are encrypted in recent commits
git show HEAD:docs/involved_parties.md | head -c 100
# Should show binary gibberish if encrypted

# Check that files are readable when unlocked
cat docs/involved_parties.md
# Should be readable (you're unlocked)
```

### Step 7: Export New Encryption Key

```bash
# Export encryption key
git-crypt export-key ~/git-crypt-stop-azs-NEW.key

# Verify export
ls -lh ~/git-crypt-stop-azs-NEW.key
# Should be ~32-64 bytes

# Backup the key
cp ~/git-crypt-stop-azs-NEW.key ~/Dropbox/encrypted/
# Also add to password manager
```

### Step 8: Force Push Rewritten History

⚠️ **Critical Step**: This overwrites remote history.

```bash
# Push all branches with force
git push origin --force --all

# Push all tags
git push origin --force --tags

# If you have protection on main branch, temporarily disable it:
# GitHub → Settings → Branches → Edit main → Temporarily disable protection
# Then re-enable after push completes
```

### Step 9: Verify Remote Encryption

```bash
# Clone fresh copy to verify
cd /tmp
git clone https://github.com/stopazus/stop-azs.git stop-azs-verify
cd stop-azs-verify

# Try to read encrypted file WITHOUT unlocking
cat docs/involved_parties.md 2>/dev/null || echo "File appears encrypted!"

# Unlock and verify
git-crypt unlock ~/git-crypt-stop-azs-NEW.key
cat docs/involved_parties.md
# Should be readable now

# Check GitHub web interface
# Browse to docs/involved_parties.md on GitHub
# Should show binary/encrypted content
```

---

## Post-Migration Steps

### Step 10: Update Team

Send notification:
```
Subject: Git Repository Encryption Migration - COMPLETE

Migration is complete. REQUIRED ACTIONS:

1. DELETE your local clone:
   rm -rf /path/to/stop-azs

2. Re-clone repository:
   git clone https://github.com/stopazus/stop-azs.git
   cd stop-azs

3. Unlock with NEW encryption key (sent separately):
   git-crypt unlock /path/to/git-crypt-stop-azs-NEW.key

4. Verify:
   git-crypt status

DO NOT try to pull/rebase your old clone - delete and re-clone!
```

### Step 11: Share New Encryption Key

Share `git-crypt-stop-azs-NEW.key` securely:
- Password manager sharing
- Encrypted email (GPG)
- Signal/WhatsApp
- **NEVER** plain email or Slack

### Step 12: Recreate Pull Requests

For each open PR noted during pre-migration:
1. Create new branch from new main
2. Cherry-pick commits (may need to resolve conflicts)
3. Open new PR
4. Close old PR with note: "Recreated as #XXX after encryption migration"

### Step 13: Re-enable CI/CD

```bash
# Re-enable GitHub Actions
# GitHub → Settings → Actions → Enable

# Re-enable branch protection
# GitHub → Settings → Branches → main → Re-enable protection

# Trigger test CI run
git commit --allow-empty -m "test: trigger CI after migration"
git push origin main
```

### Step 14: Cleanup

```bash
# Remove local backup clones
rm -rf /tmp/stop-azs-rewrite
rm -rf /tmp/stop-azs-verify

# Keep backup branch on remote for 30 days
# Then delete:
git push origin --delete backup-pre-encryption-YYYYMMDD
```

---

## Rollback Procedure

If something goes wrong during migration:

### Before Force-Push

```bash
# Reset to backup
git reset --hard backup-pre-encryption-$(date +%Y%m%d)

# Remove git-crypt
rm -rf .git/git-crypt
git-crypt init  # Start over
```

### After Force-Push (⚠️ Difficult)

```bash
# Force-push backup branch back to main
git push origin backup-pre-encryption-YYYYMMDD:main --force

# Notify team
# Everyone must delete and re-clone AGAIN
```

**Prevention**: Test the migration on a fork or separate branch first!

---

## Common Issues

### Issue: "Paths are already encrypted"

**Cause**: Git-crypt already initialized before filter-repo

**Solution**:
```bash
# Remove git-crypt state
rm -rf .git/git-crypt

# Re-initialize
git-crypt init

# Re-run filter-repo
```

### Issue: "Force-push rejected"

**Cause**: Branch protection enabled

**Solution**:
```bash
# Temporarily disable branch protection on GitHub
# Settings → Branches → main → Edit → Disable protection
# Re-run push
git push origin --force --all
# Re-enable protection
```

### Issue: "Files not encrypted after migration"

**Cause**: .gitattributes patterns don't match files

**Solution**:
```bash
# Check pattern matching
git check-attr filter docs/involved_parties.md
# Should show: docs/involved_parties.md: filter: git-crypt

# If not matching, update .gitattributes
# Re-run migration
```

### Issue: "Lost commits during filter-repo"

**Cause**: Empty commits were pruned

**Solution**:
```bash
# Use backup branch
git checkout backup-pre-encryption-YYYYMMDD

# Re-run with --prune-empty never
git filter-repo --force --prune-empty never --commit-callback '...'
```

---

## Verification Checklist

After migration, verify:

- [ ] All commit SHAs have changed
- [ ] Files on GitHub show encrypted content
- [ ] Fresh clone requires unlock
- [ ] Team members can unlock with new key
- [ ] All sensitive files are encrypted in all commits
- [ ] CI/CD works with unlocked repository
- [ ] No sensitive data visible in web interface
- [ ] Backup branch exists on remote

---

## Timeline Example

**Real-world migration timeline**:

| Time | Step | Duration |
|------|------|----------|
| T-48h | Notify team, document PRs | 30 min |
| T-24h | Verify team readiness | 15 min |
| T-0 | Start migration | - |
| +5 min | Initialize git-crypt | 5 min |
| +10 min | Run filter-repo | 10 min |
| +15 min | Verify encryption | 5 min |
| +20 min | Export key, backup | 5 min |
| +25 min | Force-push | 3 min |
| +30 min | Verify remote | 5 min |
| +35 min | Notify team | 2 min |
| +40 min | Share keys | 5 min |
| +45 min | Monitor team re-clone | ongoing |

---

## Alternative: Test Migration on Fork

**Recommended**: Practice on a fork first!

```bash
# Fork repository on GitHub
# Clone fork
git clone https://github.com/YOUR-USERNAME/stop-azs.git
cd stop-azs

# Run entire migration procedure on fork
# ... follow all steps above ...

# Verify everything works
# Then run on production repository
```

---

## Summary

Clean migration is **powerful but risky**. It gives you:

✅ **Complete encryption** of all history  
✅ **Compliance-ready** repository  
✅ **Peace of mind** for sensitive data  

But requires:

⚠️ **Team coordination**  
⚠️ **Force-push** (history rewrite)  
⚠️ **Time and care**  

**Final Recommendation**: If you're uncertain, start with [Safe Migration](ENCRYPTION_SAFE_MIGRATION.md) and upgrade to clean later if needed.

---

## Automation

These steps are automated (with safety checks) in:
```bash
./scripts/setup-git-crypt.sh  # Choose option 2
```

**The script will**:
- Confirm with "CONFIRM" prompt
- Create backups automatically
- Run all migration steps
- Verify encryption
- Provide next-steps instructions
