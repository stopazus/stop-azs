# Testing Dependabot Auto-Triage Workflows

This guide provides instructions for testing the Dependabot auto-triage workflows.

## Prerequisites

- Workflows are committed to `.github/workflows/`
- Labels are created in the repository
- Auto-merge is enabled in repository settings
- Dependabot is configured

## Test Scenarios

### Scenario 1: Patch Update (Should Auto-Merge)

**Expected Behavior:**
- ✅ Labeled with `dependencies-patch`
- ✅ Labeled with `auto-merge-candidate`
- ✅ Auto-approved
- ✅ Auto-merge enabled
- ✅ Informative comment added

**How to Test:**
1. Wait for Dependabot to create a patch update PR
2. OR manually create a test PR updating a dev dependency patch version
3. Verify labels are applied
4. Verify PR is approved
5. Verify auto-merge is enabled
6. Check that PR merges when checks pass

**Example:**
```
pytest 7.4.0 → 7.4.1
eslint 8.45.0 → 8.45.1
```

### Scenario 2: Security Update (Should Require Review)

**Expected Behavior:**
- ✅ Labeled with severity level (`security-critical`, `security-high`, etc.)
- ✅ Detailed comment with vulnerability info
- ✅ Review requested from repository owner
- ❌ NOT auto-approved
- ❌ NOT auto-merged

**How to Test:**
1. Wait for Dependabot to detect a security vulnerability
2. Verify security label is applied based on CVSS score
3. Verify comment includes:
   - Package name and versions
   - CVSS score
   - Severity level
   - Manual review requirement
4. Verify no auto-approval or auto-merge

**Example:**
```
django 3.2.0 → 3.2.20 (fixes CVE-XXXX-XXXX)
```

### Scenario 3: Major Version Update (Should Require Review)

**Expected Behavior:**
- ✅ Labeled with `dependencies-major`
- ✅ Labeled with `breaking-changes`
- ✅ Warning comment added
- ✅ Review requested
- ❌ NOT auto-approved
- ❌ NOT auto-merged

**How to Test:**
1. Wait for Dependabot to create a major version update PR
2. Verify labels are applied
3. Verify comment warns about breaking changes
4. Verify review is requested
5. Verify no auto-approval or auto-merge

**Example:**
```
fastapi 0.100.0 → 1.0.0
react 17.0.2 → 18.0.0
```

### Scenario 4: Excluded Package (Should Require Review)

**Expected Behavior:**
- ✅ Labeled appropriately for version type
- ✅ Review requested
- ❌ NOT auto-approved (even for patch)
- ❌ NOT auto-merged

**How to Test:**
1. Edit `.github/dependabot-automerge-config.yml` to exclude a package
2. Wait for or create a PR for that package
3. Verify even patch updates require review
4. Verify no auto-approval

**Example:**
```yaml
exclude_packages:
  - fastapi
  - sqlalchemy
```

### Scenario 5: Minor Version Update (Should Require Review by Default)

**Expected Behavior:**
- ✅ Labeled with `dependencies-minor`
- ✅ Informative comment added
- ❌ NOT auto-approved (by default)
- ❌ NOT auto-merged (by default)

**How to Test:**
1. Wait for Dependabot to create a minor version update PR
2. Verify correct label
3. Verify no auto-approval
4. To enable auto-merge for minor updates, edit config

**Example:**
```
pytest 7.4.0 → 7.5.0
```

## Workflow Validation

### Validate YAML Syntax

```bash
# Using Python
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/dependabot-auto-triage.yml'))"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/dependabot-pr-info.yml'))"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/dependabot-notify.yml'))"

# Using actionlint (if installed)
actionlint .github/workflows/dependabot-*.yml
```

### Trigger Manual Workflow Run

```bash
# Trigger notification workflow manually
gh workflow run dependabot-notify.yml
```

### Check Workflow Runs

```bash
# List recent workflow runs
gh run list --workflow=dependabot-auto-triage.yml --limit 10

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

## Label Verification

### Verify All Labels Exist

```bash
# List all labels
gh label list

# Check for specific labels
gh label list | grep -E "security-|dependencies-|auto-merge|breaking"
```

### Create Missing Labels

```bash
# Run the helper script
./tools/create-dependabot-labels.sh

# Or create individually
gh label create "security-critical" --color "b60205" --description "Critical security vulnerability (CVSS >= 9.0)"
```

## Notification Testing

### Test Daily Summary

1. **Manual Trigger:**
   ```bash
   gh workflow run dependabot-notify.yml
   ```

2. **Expected Output:**
   - Issue created with title "📊 Dependabot Summary - YYYY-MM-DD"
   - Labels: `dependencies`, `automation`
   - Lists all pending Dependabot PRs
   - Categorizes by type and severity

3. **Verify:**
   ```bash
   gh issue list --label "dependencies,automation"
   ```

### Test Weekly Security Report

1. **Wait for Monday 10 AM UTC** (or manually trigger)

2. **Expected Output:**
   - Issue created with title "🔒 Weekly Security Report - YYYY-WXX"
   - Lists security updates from past week
   - Categorizes by severity
   - Highlights critical/high priority items

## Mock PR Testing

If you want to test without waiting for real Dependabot PRs:

### Create a Test PR

```bash
# Create test branch
git checkout -b test/dependabot-mock-pr

# Make a small change to a dependency file
echo "# Test change" >> requirements.txt

# Commit and push
git add requirements.txt
git commit -m "test: mock dependabot update"
git push -u origin test/dependabot-mock-pr

# Create PR
gh pr create --title "Bump pytest from 7.4.0 to 7.4.1" \
  --body "Bumps pytest from 7.4.0 to 7.4.1" \
  --label "dependencies"
```

**Note:** This won't trigger as a real Dependabot PR (actor won't be `dependabot[bot]`), but you can modify the workflow condition temporarily for testing.

## Permissions Testing

### Verify Workflow Permissions

Check that workflows have necessary permissions:

```yaml
permissions:
  contents: write       # To merge PRs
  pull-requests: write  # To comment, label, and approve PRs
  issues: write         # To create summary issues
  checks: read          # To check status
```

### Test Without Sufficient Permissions

1. Remove a permission from the workflow
2. Trigger the workflow
3. Verify it fails with permission error
4. Restore the permission

## Integration Testing

### End-to-End Test Flow

1. **Setup:**
   - Ensure all workflows are committed
   - Ensure all labels exist
   - Enable auto-merge in settings

2. **Create Test Scenario:**
   - Wait for real Dependabot PR or create mock

3. **Verify Auto-Triage Workflow:**
   - PR is labeled correctly
   - Comment is added
   - Approval happens (for safe updates)
   - Auto-merge is enabled (for safe updates)

4. **Verify PR Info Workflow:**
   - Informative comment is added
   - Comment has correct information

5. **Verify Notification Workflow:**
   - Daily/weekly issues are created
   - Issues contain correct information

## Troubleshooting Tests

### Workflows Not Triggering

```bash
# Check if workflows are enabled
gh workflow list

# Enable workflow if disabled
gh workflow enable dependabot-auto-triage.yml

# Check recent runs for errors
gh run list --workflow=dependabot-auto-triage.yml
```

### Labels Not Being Applied

```bash
# Check if label exists
gh label list | grep "auto-merge-candidate"

# Create if missing
gh label create "auto-merge-candidate" --color "128a0c" --description "Safe for automatic merge"

# Check workflow logs
gh run view <run-id> --log | grep -i label
```

### Auto-Merge Not Working

1. **Verify auto-merge is enabled:**
   - Settings → General → Pull Requests → "Allow auto-merge"

2. **Check branch protection:**
   - Settings → Branches → Check rules

3. **Verify all checks pass:**
   - PR must have all required checks passing

4. **Check workflow logs:**
   ```bash
   gh run view <run-id> --log | grep -i "auto-merge"
   ```

## Success Criteria Checklist

Use this checklist to verify the implementation:

- [ ] Workflows trigger on Dependabot PRs
- [ ] Labels are applied correctly based on severity
- [ ] Labels are applied correctly based on version type
- [ ] Safe patch updates are auto-approved
- [ ] Safe patch updates have auto-merge enabled
- [ ] Security updates are NOT auto-merged
- [ ] Security updates have detailed comments
- [ ] Major version updates have warning comments
- [ ] Review requests are sent appropriately
- [ ] Informative comments are added to all PRs
- [ ] Daily summary issues are created
- [ ] Weekly security reports are created
- [ ] All workflows pass YAML validation
- [ ] No security vulnerabilities in workflows

## Continuous Testing

### Monitor Workflow Performance

```bash
# Check recent runs
gh run list --workflow=dependabot-auto-triage.yml --limit 20

# View failure rate
gh run list --workflow=dependabot-auto-triage.yml --status failure

# Check average run time
gh run list --workflow=dependabot-auto-triage.yml --json conclusion,createdAt,updatedAt
```

### Review Auto-Merged PRs

```bash
# List recently merged Dependabot PRs
gh pr list --author "dependabot[bot]" --state merged --limit 20

# Check if they were auto-merged appropriately
gh pr view <pr-number> --json labels,reviews,mergedBy
```

## Documentation

After testing, document:
- Test results
- Any issues found
- Configuration adjustments made
- Lessons learned

## Next Steps

After successful testing:
1. Monitor for a week to ensure stability
2. Adjust configuration as needed
3. Add more packages to exclusion list if needed
4. Consider enabling minor version auto-merge
5. Share results with team
