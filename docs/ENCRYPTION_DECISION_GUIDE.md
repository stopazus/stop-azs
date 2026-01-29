# Git-Crypt Migration: Decision Guide

## 🎯 Which Migration Path Should You Choose?

This guide helps you decide between **Safe Migration** (non-destructive) and **Clean Migration** (history rewrite).

---

## Quick Decision Tree

```
START HERE
    |
    ├─ Has sensitive data been committed in the past?
    |   |
    |   ├─ NO → Safe Migration (Easy choice!)
    |   |
    |   └─ YES → Continue...
    |
    ├─ Is the repository public?
    |   |
    |   ├─ YES → Clean Migration REQUIRED
    |   |         (Sensitive data is already exposed!)
    |   |
    |   └─ NO → Continue...
    |
    ├─ Do you have team members actively working?
    |   |
    |   ├─ YES → Safe Migration
    |   |         (Avoid disrupting team)
    |   |
    |   └─ NO → Continue...
    |
    ├─ Is the sensitive data highly critical?
    |   |
    |   ├─ Passwords/API keys → Clean Migration
    |   ├─ PII/Legal docs    → Clean Migration
    |   └─ Low sensitivity   → Safe Migration
    |
    └─ How much time do you have?
        |
        ├─ 5 minutes     → Safe Migration
        └─ 30-45 minutes → Clean Migration
```

---

## Path Comparison

| Factor | Safe Migration | Clean Migration |
|--------|----------------|-----------------|
| **Time Required** | ⏱️ 5 minutes | ⏱️ 30-45 minutes |
| **Complexity** | ✅ Simple | ⚠️ Advanced |
| **Team Disruption** | ✅ None | 🔥 High (force-push) |
| **History Changed** | ✅ No | 🔥 Yes (entire rewrite) |
| **Old Commits** | ⚠️ Stay unencrypted | ✅ Fully encrypted |
| **Rollback** | ✅ Easy | ⚠️ Difficult |
| **Risk Level** | ✅ Low | ⚠️ Medium-High |

---

## Safe Migration (Recommended for Most Cases)

### ✅ Choose Safe Migration If:

- You want **minimal disruption**
- Team members are **actively working**
- Sensitive data is **not yet committed** or **low severity**
- You need to **start encrypting quickly**
- You're **new to git-crypt**
- Repository is **private** and access-controlled

### ⚠️ Limitations:

- Old commits remain unencrypted in git history
- Anyone with repository access can still see old unencrypted data
- Not suitable if sensitive data is already in public history

### 📖 What Happens:

1. Initialize git-crypt
2. Configure `.gitattributes`
3. Commit configuration
4. From this point forward, matching files are encrypted
5. Old commits are untouched

### 🔒 Security Posture:

- **Future commits**: ✅ Fully encrypted
- **Current working tree**: ✅ Can be encrypted
- **Historical commits**: ❌ Remain unencrypted
- **Best for**: New secrets, going-forward protection

---

## Clean Migration (Advanced, High Security)

### ✅ Choose Clean Migration If:

- Sensitive data **already exists** in git history
- Repository is or was **public**
- You need **complete encryption** of all history
- You can coordinate a **force-push** with team
- You have **30-45 minutes** available
- Security requirements are **strict**

### ⚠️ Consequences:

- 🔥 **Rewrites entire git history** (changes all commit SHAs)
- 🔥 **Requires force-push** to remote
- 🔥 **Team must delete and re-clone** repository
- 🔥 **Breaks all pull requests** (must recreate)
- 🔥 **Breaks external references** to commit SHAs
- 🔥 **Cannot be easily undone**

### 📖 What Happens:

1. Create backup branch
2. Initialize git-crypt
3. Use `git filter-repo` to rewrite history
4. Re-encrypt all files matching `.gitattributes`
5. Force-push rewritten history
6. Team re-clones repository

### 🔒 Security Posture:

- **Future commits**: ✅ Fully encrypted
- **Current working tree**: ✅ Fully encrypted
- **Historical commits**: ✅ Fully encrypted
- **Best for**: Already-committed secrets, compliance requirements

---

## Detailed Scenarios

### Scenario 1: New Repository, No Sensitive Data Yet

**Recommendation**: **Safe Migration**

You're setting up encryption before adding sensitive data. Simple choice!

```bash
./scripts/setup-git-crypt.sh
# Choose option 1 (Safe Migration)
```

---

### Scenario 2: Private Repo, Passwords Committed Last Week

**Recommendation**: **Clean Migration**

Even in a private repo, committed passwords should be considered compromised.

**Action Plan**:
1. Rotate all committed passwords FIRST
2. Run clean migration to remove from history
3. Update systems with new passwords

```bash
# After rotating passwords
./scripts/setup-git-crypt.sh
# Choose option 2 (Clean Migration)
```

---

### Scenario 3: Public Repo, Secrets Accidentally Pushed

**Recommendation**: **Clean Migration + Immediate Rotation**

🚨 **URGENT ACTION REQUIRED**

1. **Immediately rotate all exposed secrets**
2. **Assume secrets are compromised**
3. **Run clean migration** to prevent future access
4. **Consider making repository private**

```bash
# Rotate secrets FIRST (they're already compromised!)
# Then clean migration
./scripts/setup-git-crypt.sh
# Choose option 2 (Clean Migration)
```

**Note**: Clean migration does NOT retroactively protect already-cloned data!

---

### Scenario 4: Active Team, Investigation Docs Not Yet Added

**Recommendation**: **Safe Migration**

Team is working, you haven't added sensitive files yet. Perfect for safe migration.

```bash
./scripts/setup-git-crypt.sh
# Choose option 1 (Safe Migration)
```

---

### Scenario 5: Solo Developer, PII in History

**Recommendation**: **Clean Migration**

No team coordination needed, and PII compliance requires removal from history.

```bash
./scripts/setup-git-crypt.sh
# Choose option 2 (Clean Migration)
```

---

### Scenario 6: Large Team, Production Credentials in History

**Recommendation**: **Clean Migration (Scheduled)**

1. **Rotate credentials immediately**
2. **Schedule clean migration** during low-activity period
3. **Notify team 48 hours in advance**
4. **Coordinate the re-clone**

```bash
# During scheduled maintenance window
./scripts/setup-git-crypt.sh
# Choose option 2 (Clean Migration)
```

---

## Decision Checklist

Use this checklist to make your decision:

### For Safe Migration:

- [ ] No sensitive data in current git history, OR
- [ ] Sensitive data in history is low-severity, AND
- [ ] Repository is private with access control, AND
- [ ] Team is actively working (disruption not acceptable), AND
- [ ] You need encryption active in under 5 minutes

**If all checked**: ✅ **Safe Migration**

---

### For Clean Migration:

- [ ] Sensitive data exists in git history, AND one or more of:
  - [ ] Repository is or was public
  - [ ] Data is high-severity (passwords, keys, PII)
  - [ ] Compliance requires history encryption
  - [ ] Security policy requires complete encryption
- [ ] You have 30-45 minutes available
- [ ] You can coordinate force-push with team
- [ ] You understand the risks and consequences

**If these apply**: 🔥 **Clean Migration**

---

## Still Unsure?

### Start with Safe Migration if:

- You're uncertain
- You're new to git-crypt
- You want to test first
- Timeline is tight

You can always do a clean migration later if needed.

### Get Help:

- Review the detailed guides:
  - [Safe Migration Guide](ENCRYPTION_SAFE_MIGRATION.md)
  - [Clean Migration Guide](ENCRYPTION_CLEAN_MIGRATION.md)
- Ask repository maintainers (@stopazus)
- Start with safe migration, evaluate, upgrade to clean if needed

---

## Next Steps

Once you've decided:

1. **Safe Migration**: Read [ENCRYPTION_SAFE_MIGRATION.md](ENCRYPTION_SAFE_MIGRATION.md)
2. **Clean Migration**: Read [ENCRYPTION_CLEAN_MIGRATION.md](ENCRYPTION_CLEAN_MIGRATION.md)
3. **Run the wizard**: `./scripts/setup-git-crypt.sh`

---

## Key Takeaway

> **Safe Migration** = Fast, safe, encrypts going forward  
> **Clean Migration** = Slow, risky, encrypts everything including history

When in doubt, start safe. You can always upgrade to clean later.
