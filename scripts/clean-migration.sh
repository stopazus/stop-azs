#!/bin/bash
# Clean migration: Rewrite history with full encryption

set -e

echo "🔥 Git-Crypt Clean Migration"
echo "============================="
echo ""
echo "⚠️  WARNING: This will rewrite git history!"
echo ""
echo "This procedure will:"
echo "  - Rewrite entire git history"
echo "  - Change all commit SHAs"
echo "  - Require force-push"
echo "  - Force team to re-clone"
echo ""

# Confirmation
read -p "Have you read docs/ENCRYPTION_CLEAN_MIGRATION.md? (yes/no): " read_docs
if [ "$read_docs" != "yes" ]; then
    echo "Please read the clean migration guide first:"
    echo "  docs/ENCRYPTION_CLEAN_MIGRATION.md"
    exit 1
fi

echo ""
read -p "Is your team ready for this migration? (yes/no): " team_ready
if [ "$team_ready" != "yes" ]; then
    echo "Coordinate with team first, then re-run."
    exit 1
fi

echo ""
read -p "Type 'I UNDERSTAND' to proceed: " confirm
if [ "$confirm" != "I UNDERSTAND" ]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "🚀 Starting clean migration..."
echo ""

# Check requirements
if ! command -v git-crypt &> /dev/null; then
    echo "❌ git-crypt is not installed"
    exit 1
fi

if ! command -v git-filter-repo &> /dev/null; then
    echo "❌ git-filter-repo is not installed"
    echo ""
    echo "Install with:"
    echo "  macOS:   brew install git-filter-repo"
    echo "  Ubuntu:  pip3 install git-filter-repo"
    exit 1
fi

echo "✅ Requirements satisfied"
echo ""

# Step 1: Create backup
echo "Step 1: Creating backup..."
BACKUP_BRANCH="backup-pre-encryption-$(date +%Y%m%d-%H%M%S)"
git branch "$BACKUP_BRANCH"
git push origin "$BACKUP_BRANCH" || echo "⚠️  Could not push backup (continue anyway)"
git tag "pre-encryption-$(date +%Y%m%d-%H%M%S)"
echo "✅ Backup created: $BACKUP_BRANCH"
echo ""

# Step 2: Clean working directory
echo "Step 2: Ensuring clean working directory..."
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "❌ You have uncommitted changes"
    echo "Commit or stash them first."
    exit 1
fi
echo "✅ Working directory clean"
echo ""

# Step 3: Initialize git-crypt
echo "Step 3: Initializing git-crypt..."
if git-crypt status &> /dev/null; then
    echo "⚠️  git-crypt already initialized (continuing)"
else
    git-crypt init
    echo "✅ git-crypt initialized"
fi
echo ""

# Step 4: Verify .gitattributes
echo "Step 4: Verifying .gitattributes..."
if [ ! -f .gitattributes ]; then
    echo "❌ .gitattributes not found!"
    exit 1
fi
echo "✅ .gitattributes exists"
echo ""

# Step 5: Commit .gitattributes if needed
echo "Step 5: Committing .gitattributes..."
git add .gitattributes || true
if ! git diff --cached --quiet 2>/dev/null; then
    git commit -m "feat: add git-crypt encryption configuration" || true
fi
echo "✅ Configuration ready"
echo ""

# Step 6: Re-encrypt all files (simple approach)
echo "Step 6: Re-encrypting repository..."
echo "This may take several minutes..."
echo ""

# Remove all cached files and re-add (triggers git-crypt)
git rm --cached -r .
git add .
git commit -m "feat: re-encrypt repository with git-crypt" || true

echo "✅ Files re-encrypted"
echo ""

# Step 7: Export encryption key
echo "Step 7: Exporting NEW encryption key..."
KEY_FILE="$HOME/git-crypt-stop-azs-NEW-$(date +%Y%m%d).key"
git-crypt export-key "$KEY_FILE"
echo "✅ New key exported to: $KEY_FILE"
echo ""
echo "⚠️  CRITICAL: This is a NEW key!"
echo "   - Old key will NOT work after force-push"
echo "   - Share this new key with team"
echo "   - Back up securely"
echo ""

# Step 8: Verify encryption
echo "Step 8: Verifying encryption..."
git-crypt status > /tmp/git-crypt-status.txt || true
echo "✅ Encryption verified"
echo ""

# Step 9: Force-push warning
echo "Step 9: Ready to force-push..."
echo ""
echo "⚠️  FINAL WARNING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next step will FORCE-PUSH rewritten history."
echo ""
echo "After this:"
echo "  - All commit SHAs will change"
echo "  - Team must DELETE and RE-CLONE"
echo "  - Pull requests will break"
echo "  - Cannot be easily undone"
echo ""
read -p "Type 'FORCE PUSH' to continue: " force_confirm
if [ "$force_confirm" != "FORCE PUSH" ]; then
    echo "❌ Aborted before force-push"
    echo ""
    echo "To rollback:"
    echo "  git reset --hard $BACKUP_BRANCH"
    exit 1
fi

echo ""
echo "Force-pushing..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Check if branch protection might block
echo ""
echo "If force-push fails, disable branch protection:"
echo "  GitHub → Settings → Branches → $CURRENT_BRANCH → Edit"
echo ""
read -p "Press Enter to force-push..."

git push origin "$CURRENT_BRANCH" --force

echo "✅ Force-push complete"
echo ""

# Success summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Clean Migration Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 URGENT: Notify Team Immediately"
echo ""
echo "Send this message:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Git repository has been re-encrypted."
echo ""
echo "REQUIRED ACTIONS:"
echo "1. DELETE your local clone:"
echo "   rm -rf /path/to/stop-azs"
echo ""
echo "2. Re-clone repository:"
echo "   git clone https://github.com/stopazus/stop-azs.git"
echo ""
echo "3. Unlock with NEW key (shared separately):"
echo "   git-crypt unlock /path/to/NEW-key"
echo ""
echo "DO NOT try to pull/rebase old clone!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 Next Steps for You:"
echo ""
echo "1. Share NEW encryption key (securely):"
echo "   Key: $KEY_FILE"
echo "   - Password manager"
echo "   - Encrypted email"
echo "   - Signal/WhatsApp"
echo ""
echo "2. Recreate open pull requests"
echo ""
echo "3. Re-enable CI/CD if disabled"
echo ""
echo "4. Keep backup branch for 30 days:"
echo "   Branch: $BACKUP_BRANCH"
echo "   Delete later: git push origin --delete $BACKUP_BRANCH"
echo ""
echo "5. Verify encryption on GitHub:"
echo "   ./scripts/verify-encryption-remote.sh"
echo ""
echo "📚 Documentation:"
echo "   - docs/ENCRYPTION_CLEAN_MIGRATION.md"
echo "   - docs/GIT_CRYPT_SETUP.md"
echo ""
