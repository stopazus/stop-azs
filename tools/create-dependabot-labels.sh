#!/bin/bash
# Script to create all required labels for Dependabot auto-triage workflows
# Usage: ./create-dependabot-labels.sh

set -e

echo "Creating labels for Dependabot auto-triage workflows..."
echo ""

# Security severity labels
echo "Creating security severity labels..."
gh label create "security-critical" --color "b60205" --description "Critical security vulnerability (CVSS >= 9.0)" --force
gh label create "security-high" --color "d93f0b" --description "High severity security issue (CVSS >= 7.0)" --force
gh label create "security-medium" --color "fbca04" --description "Medium severity security issue (CVSS >= 4.0)" --force
gh label create "security-low" --color "0e8a16" --description "Low severity security issue" --force

# Version update labels
echo "Creating version update labels..."
gh label create "dependencies-patch" --color "e99695" --description "Patch version dependency update" --force
gh label create "dependencies-minor" --color "f9d0c4" --description "Minor version dependency update" --force
gh label create "dependencies-major" --color "d73a4a" --description "Major version dependency update" --force

# Status labels
echo "Creating status labels..."
gh label create "auto-merge-candidate" --color "128a0c" --description "Safe for automatic merge" --force
gh label create "breaking-changes" --color "d4c5f9" --description "May contain breaking changes" --force

# General labels
echo "Creating general labels..."
gh label create "dependencies" --color "0366d6" --description "Pull requests that update a dependency file" --force
gh label create "automation" --color "ededed" --description "Automated processes and workflows" --force

echo ""
echo "✅ All labels created successfully!"
echo ""
echo "Labels created:"
gh label list | grep -E "security-|dependencies-|auto-merge|breaking-changes|automation"
