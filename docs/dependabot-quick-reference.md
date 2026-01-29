# Dependabot Auto-Triage - Quick Reference

## 🚀 Quick Start

### 1. Enable Dependabot
Copy `.github/dependabot.yml.sample` to `.github/dependabot.yml`

### 2. Create Labels
Run the helper script:
```bash
./tools/create-dependabot-labels.sh
```

### 3. Enable Auto-Merge
Go to **Settings** → **General** → **Pull Requests**
- ✅ Allow auto-merge
- ✅ Automatically delete head branches

## 📋 Workflow Summary

| Workflow | Purpose | Triggers |
|----------|---------|----------|
| **Auto-Triage** | Classifies, labels, auto-approves | PR opened/updated/labeled |
| **PR Info** | Adds informative comments | PR opened |
| **Notifications** | Daily/weekly reports | Schedule (cron) |

## 🏷️ Label Guide

### Security Severity
- 🔴 `security-critical` - CVSS ≥ 9.0
- 🟠 `security-high` - CVSS ≥ 7.0
- 🟡 `security-medium` - CVSS ≥ 4.0
- 🟢 `security-low` - CVSS < 4.0

### Version Updates
- `dependencies-patch` - 1.0.0 → 1.0.1
- `dependencies-minor` - 1.0.0 → 1.1.0
- `dependencies-major` - 1.0.0 → 2.0.0

### Status
- `auto-merge-candidate` - Safe for auto-merge
- `breaking-changes` - Manual review required

## ✅ Auto-Merge Criteria

**Automatically merged if ALL:**
- ✓ Patch version update
- ✓ NOT a security update
- ✓ NOT in exclusion list
- ✓ All checks pass
- ✓ Dev dependency OR not excluded

**NEVER auto-merged:**
- ✗ Security updates (any CVSS)
- ✗ Major version updates
- ✗ Excluded packages (see config)

## 🔒 Security Behavior

| Update Type | Auto-Approve | Auto-Merge | Review Required |
|-------------|--------------|------------|-----------------|
| Security (any) | ✗ | ✗ | ✓ |
| Major version | ✗ | ✗ | ✓ |
| Minor version | ✗ | ✗ | ✓ |
| Patch (excluded pkg) | ✗ | ✗ | ✓ |
| Patch (dev dep) | ✓ | ✓ | ✗ |
| Patch (non-excluded) | ✓ | ✓ | ✗ |

## ⚙️ Configuration Files

| File | Purpose |
|------|---------|
| `.github/dependabot-automerge-config.yml` | Auto-merge behavior |
| `.github/labels.yml` | Label definitions |
| `.github/dependabot.yml` | Dependabot configuration |

## 🛠️ Customization

### Exclude a Package
Edit `.github/dependabot-automerge-config.yml`:
```yaml
exclude_packages:
  - your-package-name
```

### Change Security Thresholds
```yaml
security:
  critical_cvss: 9.0
  high_cvss: 7.0
  medium_cvss: 4.0
```

### Enable Minor Version Auto-Merge
```yaml
auto_merge_update_types:
  - "version-update:semver-patch"
  - "version-update:semver-minor"  # Add this
```

## 🔍 Monitoring

### Daily Summary
- **When:** Daily at 9 AM UTC
- **What:** Issue with pending PRs count and list
- **Labels:** `dependencies`, `automation`

### Weekly Security Report
- **When:** Mondays at 10 AM UTC
- **What:** Security updates from past week
- **Labels:** `security`, `dependencies`, `automation`

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Workflows not triggering | Check Dependabot is enabled |
| Labels not applied | Run `./tools/create-dependabot-labels.sh` |
| Auto-merge not working | Enable in repository settings |
| Permission errors | Check workflow has required permissions |

## 📚 Documentation

- **Setup Guide:** `docs/dependabot-setup.md`
- **README:** Main overview and features
- **This File:** Quick reference

## 🔗 Useful Commands

```bash
# List all open Dependabot PRs
gh pr list --author "dependabot[bot]" --state open

# List security PRs
gh pr list --label "security-critical,security-high"

# Manually trigger notification workflow
gh workflow run dependabot-notify.yml

# Check workflow runs
gh run list --workflow=dependabot-auto-triage.yml
```

## 📞 Support

For detailed setup instructions, see `docs/dependabot-setup.md`
