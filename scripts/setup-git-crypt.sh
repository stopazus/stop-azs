#!/bin/bash
# Interactive git-crypt setup wizard

set -e

echo "🔐 Git-Crypt Setup Wizard"
echo "========================="
echo ""

# Check git-crypt installation
if ! command -v git-crypt &> /dev/null; then
    echo "❌ git-crypt is not installed"
    echo ""
    echo "Install with:"
    echo "  macOS:   brew install git-crypt"
    echo "  Ubuntu:  sudo apt-get install git-crypt"
    echo "  Windows: Use WSL or download from releases"
    echo ""
    exit 1
fi

echo "✅ git-crypt is installed ($(git-crypt --version))"
echo ""

# Check if already initialized
if git-crypt status &> /dev/null; then
    echo "⚠️  git-crypt is already initialized"
    echo ""
    read -p "Continue anyway? (yes/no): " cont
    if [ "$cont" != "yes" ]; then
        exit 0
    fi
fi

echo "📖 Migration Path Options:"
echo ""
echo "  1) Safe Migration (Recommended)"
echo "     ⏱️  5 minutes"
echo "     ✅ No history changes"
echo "     ✅ No team disruption"
echo "     ⚠️  Old commits stay unencrypted"
echo ""
echo "  2) Clean Migration (Advanced)"
echo "     ⏱️  30-45 minutes"
echo "     🔥 Rewrites entire history"
echo "     ⚠️  Requires force-push"
echo "     ⚠️  Team must re-clone"
echo ""
echo "  3) Review Docs First"
echo "     📚 Read migration guides"
echo "     🤔 Decide later"
echo ""

read -p "Choose (1/2/3): " choice

case $choice in
  1)
    echo ""
    echo "✅ Starting Safe Migration..."
    ./scripts/safe-migration.sh
    ;;
  2)
    echo ""
    echo "⚠️  Starting Clean Migration..."
    echo ""
    echo "This will rewrite git history. Are you SURE?"
    read -p "Type 'CONFIRM' to proceed: " confirm
    if [ "$confirm" = "CONFIRM" ]; then
        ./scripts/clean-migration.sh
    else
        echo "❌ Aborted"
        exit 1
    fi
    ;;
  3)
    echo ""
    echo "📚 Review these guides:"
    echo "  - docs/ENCRYPTION_DECISION_GUIDE.md"
    echo "  - docs/ENCRYPTION_SAFE_MIGRATION.md"
    echo "  - docs/ENCRYPTION_CLEAN_MIGRATION.md"
    echo ""
    echo "Run this wizard again when ready:"
    echo "  ./scripts/setup-git-crypt.sh"
    ;;
  *)
    echo "❌ Invalid choice"
    exit 1
    ;;
esac
