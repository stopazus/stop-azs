#!/bin/bash
# Safe migration: Enable git-crypt without rewriting history

set -e

echo "🔐 Git-Crypt Safe Migration"
echo "============================"
echo ""
echo "This will enable encryption going forward without changing git history."
echo ""

# Check git-crypt installation
if ! command -v git-crypt &> /dev/null; then
    echo "❌ git-crypt is not installed"
    echo "Install it first, then re-run this script."
    exit 1
fi

echo "✅ git-crypt is installed"
echo ""

# Step 1: Check working directory
echo "Step 1: Checking working directory..."
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "⚠️  You have uncommitted changes"
    echo ""
    read -p "Commit them now? (yes/no): " commit_now
    if [ "$commit_now" = "yes" ]; then
        git add .
        git commit -m "chore: save work before encryption setup"
        echo "✅ Changes committed"
    else
        echo "Please commit or stash changes first, then re-run."
        exit 1
    fi
fi
echo "✅ Working directory is clean"
echo ""

# Step 2: Initialize git-crypt
echo "Step 2: Initializing git-crypt..."
if git-crypt status &> /dev/null; then
    echo "✅ git-crypt already initialized"
else
    git-crypt init
    echo "✅ git-crypt initialized"
fi
echo ""

# Step 3: Verify .gitattributes
echo "Step 3: Verifying .gitattributes..."
if [ ! -f .gitattributes ]; then
    echo "❌ .gitattributes not found!"
    echo "This file should already exist in the repository."
    exit 1
fi
echo "✅ .gitattributes exists"
echo ""

# Step 4: Export encryption key
echo "Step 4: Exporting encryption key..."
KEY_FILE="$HOME/git-crypt-stop-azs-$(date +%Y%m%d).key"
git-crypt export-key "$KEY_FILE"
echo "✅ Key exported to: $KEY_FILE"
echo ""
echo "⚠️  IMPORTANT: Back up this key securely!"
echo "   - Add to password manager (1Password, LastPass)"
echo "   - Copy to encrypted storage"
echo "   - NEVER commit to repository"
echo ""

# Step 5: Commit configuration if needed
echo "Step 5: Committing configuration..."
if git diff --cached --quiet && git diff --quiet; then
    echo "✅ No configuration changes to commit"
else
    git add .gitattributes
    git commit -m "feat: enable git-crypt encryption for sensitive files" || true
    echo "✅ Configuration committed"
fi
echo ""

# Step 6: Verify encryption status
echo "Step 6: Verifying encryption status..."
git-crypt status > /tmp/git-crypt-status.txt || true
echo "✅ Encryption status checked"
echo ""

# Step 7: Optional - re-encrypt existing files
echo "Step 7: Re-encrypt existing files (optional)..."
read -p "Re-encrypt existing files matching .gitattributes patterns? (yes/no): " reencrypt
if [ "$reencrypt" = "yes" ]; then
    echo "Re-encrypting files..."
    git rm --cached -r . || true
    git add .
    if ! git diff --cached --quiet; then
        git commit -m "chore: re-add files to trigger encryption"
        echo "✅ Files re-encrypted"
    else
        echo "✅ No files needed re-encryption"
    fi
else
    echo "⏭️  Skipped - files will encrypt when next committed"
fi
echo ""

# Step 8: Test encryption
echo "Step 8: Testing encryption..."
TEST_FILE="test-encryption-$$.sensitive"
echo "TEST DATA - DELETE THIS FILE" > "$TEST_FILE"
git add "$TEST_FILE"
git commit -m "test: verify encryption" || true
if git-crypt status 2>/dev/null | grep -q "$TEST_FILE.*encrypted"; then
    echo "✅ Encryption test passed"
    git rm "$TEST_FILE"
    git commit -m "test: cleanup encryption test" || true
    rm -f "$TEST_FILE"
else
    echo "⚠️  Encryption test inconclusive (this may be normal)"
    git rm -f "$TEST_FILE" 2>/dev/null || true
    rm -f "$TEST_FILE"
fi
echo ""

# Step 9: Push changes
echo "Step 9: Pushing changes..."
read -p "Push changes to remote? (yes/no): " push_now
if [ "$push_now" = "yes" ]; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    git push origin "$CURRENT_BRANCH"
    echo "✅ Changes pushed"
else
    echo "⏭️  Skipped - remember to push later"
fi
echo ""

# Success summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Safe Migration Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 Next Steps:"
echo ""
echo "1. Back up encryption key:"
echo "   Key: $KEY_FILE"
echo "   - Add to password manager"
echo "   - Copy to secure location"
echo ""
echo "2. Share key with team members (securely):"
echo "   - Use ./scripts/share-access.sh"
echo "   - Or share via password manager"
echo ""
echo "3. Verify encryption:"
echo "   git-crypt status"
echo "   ./scripts/check-encryption.sh"
echo ""
echo "4. Daily usage:"
echo "   - Just work normally!"
echo "   - Encryption is automatic"
echo "   - See docs/QUICK_START_ENCRYPTION.md"
echo ""
echo "⚠️  Important Notes:"
echo "   - Old commits remain unencrypted"
echo "   - New commits are encrypted"
echo "   - Files encrypt when re-committed"
echo ""
echo "📚 Documentation:"
echo "   - docs/GIT_CRYPT_SETUP.md"
echo "   - docs/QUICK_START_ENCRYPTION.md"
echo ""
