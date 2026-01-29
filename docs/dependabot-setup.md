# Dependabot Auto-Triage Setup Guide

This guide explains how to set up and use the Dependabot auto-triage workflows in this repository.

## Overview

The Dependabot auto-triage system consists of three workflows that work together to manage dependency updates automatically:

1. **Auto-Triage** - Classifies, labels, and manages Dependabot PRs
2. **PR Info** - Adds informative comments to PRs
3. **Notifications** - Sends daily and weekly reports

## Prerequisites

### 1. Enable Dependabot

First, ensure Dependabot is enabled in your repository. Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

### 2. Create Required Labels

The workflows require specific labels to be created in your repository. You can create them manually or use the GitHub CLI:

```bash
# Security severity labels
gh label create "security-critical" --color "b60205" --description "Critical security vulnerability (CVSS >= 9.0)"
gh label create "security-high" --color "d93f0b" --description "High severity security issue (CVSS >= 7.0)"
gh label create "security-medium" --color "fbca04" --description "Medium severity security issue (CVSS >= 4.0)"
gh label create "security-low" --color "0e8a16" --description "Low severity security issue"

# Version update labels
gh label create "dependencies-patch" --color "e99695" --description "Patch version dependency update"
gh label create "dependencies-minor" --color "f9d0c4" --description "Minor version dependency update"
gh label create "dependencies-major" --color "d73a4a" --description "Major version dependency update"

# Status labels
gh label create "auto-merge-candidate" --color "128a0c" --description "Safe for automatic merge"
gh label create "breaking-changes" --color "d4c5f9" --description "May contain breaking changes"

# General labels
gh label create "dependencies" --color "0366d6" --description "Pull requests that update a dependency file"
gh label create "automation" --color "ededed" --description "Automated processes and workflows"
```

Alternatively, use a label sync tool like [github-label-sync](https://github.com/Financial-Times/github-label-sync) with the `.github/labels.yml` file.

### 3. Configure Repository Settings

Enable auto-merge in your repository settings:

1. Go to **Settings** → **General**
2. Scroll to **Pull Requests**
3. Check **Allow auto-merge**
4. Check **Automatically delete head branches**

### 4. Set Up Branch Protection (Optional but Recommended)

To ensure safe auto-merging:

1. Go to **Settings** → **Branches**
2. Add a rule for your default branch (e.g., `main`)
3. Enable:
   - **Require status checks to pass before merging**
   - **Require branches to be up to date before merging**
   - Add any CI/CD checks that must pass

## Configuration

### Auto-Merge Configuration

Edit `.github/dependabot-automerge-config.yml` to customize behavior:

```yaml
# Package ecosystems to enable auto-merge
enabled_ecosystems:
  - pip
  - npm
  - github-actions

# Version bump types to auto-merge (only for non-security updates)
auto_merge_update_types:
  - "version-update:semver-patch"  # 1.0.0 -> 1.0.1

# Never auto-merge these packages (require manual review)
exclude_packages:
  - fastapi  # Core API framework
  - sqlalchemy  # Database ORM
  - psycopg2  # PostgreSQL driver
  - pyjwt  # Authentication
  - cryptography  # Security library

# Auto-merge dev dependencies (testing, linting, etc.)
auto_merge_dev_dependencies: true

# Security thresholds
security:
  critical_cvss: 9.0
  high_cvss: 7.0
  medium_cvss: 4.0
  
  # Always require review for security updates
  require_review_for_security: true
```

## How It Works

### Workflow Triggers

The workflows trigger on different events:

- **Auto-Triage**: Runs when Dependabot opens, updates, or labels a PR
- **PR Info**: Runs when Dependabot opens a PR
- **Notifications**: Runs on schedule (daily and weekly)

### Auto-Merge Logic

A PR is automatically approved and merged if ALL of these conditions are met:

1. ✅ It's a patch version update (`1.0.0` → `1.0.1`)
2. ✅ It's NOT a security update
3. ✅ The package is NOT in the exclusion list
4. ✅ All required checks pass
5. ✅ It's a development dependency (for stricter security)

### Security Update Handling

Security updates are NEVER auto-merged. Instead:

1. 🏷️ Labeled with severity (`security-critical`, `security-high`, etc.)
2. 💬 Commented with vulnerability details
3. 👀 Review requested from repository owner
4. 🚫 Auto-merge disabled

### Major Version Updates

Major version updates (e.g., `1.x.x` → `2.0.0`):

1. 🏷️ Labeled with `dependencies-major` and `breaking-changes`
2. 💬 Commented with warning about breaking changes
3. 👀 Review requested
4. 🚫 Auto-merge disabled

## Testing

### Test with a Mock PR

You can test the workflows by creating a test PR:

1. Create a new branch
2. Update a dependency version in `package.json` or `requirements.txt`
3. Open a PR
4. Manually trigger the workflows or wait for Dependabot

### Validate Workflow Syntax

```bash
# Install actionlint (optional)
brew install actionlint  # macOS
# or
go install github.com/rhysd/actionlint/cmd/actionlint@latest

# Validate workflows
actionlint .github/workflows/dependabot-*.yml

# Or use Python to check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/dependabot-auto-triage.yml'))"
```

## Monitoring

### Daily Summaries

The notification workflow creates daily issues with:

- Total pending PRs
- Count by severity
- Count by update type
- List of all pending updates

### Weekly Security Reports

Every Monday, a security report is created with:

- Security updates from the past week
- Count by severity
- Action items for critical/high updates

## Troubleshooting

### Workflows Not Triggering

1. Check that Dependabot is enabled
2. Verify workflow files are in `.github/workflows/`
3. Check GitHub Actions are enabled in repository settings
4. Look at Actions tab for error messages

### Labels Not Being Applied

1. Ensure labels exist in the repository
2. Check workflow permissions in the YAML files
3. Review workflow run logs in Actions tab

### Auto-Merge Not Working

1. Verify auto-merge is enabled in repository settings
2. Check that branch protection rules allow auto-merge
3. Ensure all required status checks pass
4. Review the workflow logs for errors

### Permission Errors

The workflows require specific permissions:

```yaml
permissions:
  contents: write       # To merge PRs
  pull-requests: write  # To comment, label, and approve PRs
  issues: write         # To create summary issues
  checks: read          # To check status
```

If using a custom `GITHUB_TOKEN`, ensure it has these permissions.

## Best Practices

1. **Start Conservative**: Begin with only patch updates for dev dependencies
2. **Monitor Initially**: Watch the first few auto-merges closely
3. **Review Security Updates**: Always manually review security updates
4. **Keep Exclusion List Updated**: Add critical packages to the exclusion list
5. **Enable Branch Protection**: Require CI checks to pass before merge
6. **Regular Reviews**: Periodically review the weekly security reports

## Security Considerations

- Security updates are NEVER auto-merged
- Critical packages can be excluded from auto-merge
- All auto-merges require passing CI checks
- Review requests are sent to repository owner
- CVSS scores determine security severity

## Customization

### Disable Auto-Merge Entirely

Remove or comment out the "Enable auto-merge" step in `dependabot-auto-triage.yml`.

### Change Security Thresholds

Edit the CVSS thresholds in `.github/dependabot-automerge-config.yml`:

```yaml
security:
  critical_cvss: 9.0   # Adjust as needed
  high_cvss: 7.0
  medium_cvss: 4.0
```

### Add More Update Types

To auto-merge minor updates as well:

```yaml
auto_merge_update_types:
  - "version-update:semver-patch"
  - "version-update:semver-minor"
```

### Disable Notifications

Comment out or remove the cron schedules in `dependabot-notify.yml`.

## Support

For issues or questions:

1. Check the [GitHub Actions documentation](https://docs.github.com/en/actions)
2. Review the [Dependabot documentation](https://docs.github.com/en/code-security/dependabot)
3. Open an issue in this repository

## References

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [dependabot/fetch-metadata action](https://github.com/dependabot/fetch-metadata)
- [Semantic Versioning](https://semver.org/)
- [CVSS Scoring](https://www.first.org/cvss/)
