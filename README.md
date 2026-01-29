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

## 🤖 Automated Security Workflows

This repository uses automated workflows to manage dependency updates:

- **Auto-merge**: Safe patch updates are automatically approved and merged
- **Security triage**: Security updates are labeled and flagged for review
- **Smart labeling**: All Dependabot PRs are automatically categorized
- **Daily summaries**: Automated reports on pending dependency updates
- **Weekly security reports**: Regular security update tracking

### Workflow Details

#### Dependabot Auto-Triage
- **File**: [.github/workflows/dependabot-auto-triage.yml](.github/workflows/dependabot-auto-triage.yml)
- **Purpose**: Automatically classifies, labels, and manages Dependabot PRs
- **Features**:
  - Severity classification based on CVSS scores
  - Automatic approval for safe patch updates
  - Security update flagging and review requests
  - Auto-merge for approved safe updates

#### Dependabot PR Info
- **File**: [.github/workflows/dependabot-pr-info.yml](.github/workflows/dependabot-pr-info.yml)
- **Purpose**: Adds informative comments to Dependabot PRs
- **Features**: Detailed update summaries with security information

#### Dependabot Notifications
- **File**: [.github/workflows/dependabot-notify.yml](.github/workflows/dependabot-notify.yml)
- **Purpose**: Provides daily and weekly dependency update reports
- **Features**: Automated issue creation for tracking pending updates

### Configuration

The auto-merge behavior can be customized in [.github/dependabot-automerge-config.yml](.github/dependabot-automerge-config.yml).

### Labels

The workflows use several labels for categorization. See [.github/labels.yml](.github/labels.yml) for the complete list and create them in your repository settings.

## Testing

The project currently has no automated test suite. A `pytest` run (August 2025) reports zero
collected tests, confirming that no executable checks are defined yet.
