#!/bin/bash
# Check git-crypt encryption status

set -e

echo "🔍 Git-Crypt Encryption Status"
echo "==============================="
echo ""

# Check git-crypt installation
if ! command -v git-crypt &> /dev/null; then
    echo "❌ git-crypt is not installed"
    echo ""
    echo "Install with:"
    echo "  macOS:   brew install git-crypt"
    echo "  Ubuntu:  sudo apt-get install git-crypt"
    exit 1
fi

# Check if git-crypt is initialized
if ! git-crypt status &> /dev/null 2>&1; then
    echo "❌ git-crypt is not initialized in this repository"
    echo ""
    echo "Initialize with:"
    echo "  ./scripts/setup-git-crypt.sh"
    exit 1
fi

echo "✅ git-crypt is initialized"
echo ""

# Check if repository is locked or unlocked
echo "📊 Repository Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Try to determine lock status by checking a known encrypted file
if [ -f "docs/involved_parties.md" ]; then
    if git-crypt status 2>&1 | grep -q "docs/involved_parties.md.*encrypted"; then
        # File should be encrypted
        if file docs/involved_parties.md 2>/dev/null | grep -q "text"; then
            echo "🔓 Repository: UNLOCKED (files are readable)"
        else
            echo "🔒 Repository: LOCKED (files are encrypted)"
        fi
    fi
else
    # No known encrypted files exist yet
    if git-crypt status 2>&1 | grep -q "not encrypted"; then
        echo "🔓 Repository: UNLOCKED"
    else
        echo "🔒 Repository: LOCKED"
    fi
fi
echo ""

# Show encryption patterns
echo "🎯 Encryption Patterns (.gitattributes):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f .gitattributes ]; then
    grep "filter=git-crypt" .gitattributes | head -10
    PATTERN_COUNT=$(grep -c "filter=git-crypt" .gitattributes || echo "0")
    echo ""
    echo "Total patterns: $PATTERN_COUNT"
else
    echo "⚠️  .gitattributes not found"
fi
echo ""

# Show encrypted files
echo "🔐 Encrypted Files:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ENCRYPTED_FILES=$(git-crypt status 2>&1 | grep "encrypted:" | wc -l | tr -d ' ')
if [ "$ENCRYPTED_FILES" -gt 0 ]; then
    echo "Found $ENCRYPTED_FILES encrypted file(s):"
    echo ""
    git-crypt status 2>&1 | grep "encrypted:" | head -20
    if [ "$ENCRYPTED_FILES" -gt 20 ]; then
        echo "..."
        echo "(showing first 20 of $ENCRYPTED_FILES files)"
    fi
else
    echo "No files currently encrypted"
    echo "(Files will encrypt when committed)"
fi
echo ""

# Show unencrypted files (limited output)
echo "📄 Sample Unencrypted Files:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
UNENCRYPTED_COUNT=$(git-crypt status 2>&1 | grep "not encrypted:" | wc -l | tr -d ' ')
if [ "$UNENCRYPTED_COUNT" -gt 0 ]; then
    echo "Found $UNENCRYPTED_COUNT unencrypted file(s)"
    echo "(showing first 10):"
    echo ""
    git-crypt status 2>&1 | grep "not encrypted:" | head -10
else
    echo "All tracked files are encrypted"
fi
echo ""

# Check for files that SHOULD be encrypted but aren't
echo "⚠️  Verification:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ISSUES=0

# Check if involved_parties.md exists and is encrypted
if [ -f "docs/involved_parties.md" ]; then
    if git-crypt status 2>&1 | grep "docs/involved_parties.md" | grep -q "encrypted"; then
        echo "✅ docs/involved_parties.md is encrypted"
    else
        echo "❌ docs/involved_parties.md is NOT encrypted"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo "ℹ️  docs/involved_parties.md does not exist yet"
fi

# Check for .env.production
if [ -f ".env.production" ]; then
    if git-crypt status 2>&1 | grep ".env.production" | grep -q "encrypted"; then
        echo "✅ .env.production is encrypted"
    else
        echo "❌ .env.production is NOT encrypted"
        ISSUES=$((ISSUES + 1))
    fi
fi

# Check for common sensitive patterns
for pattern in "*.pem" "*.key" "secrets/*" "evidence/*"; do
    # Find files matching pattern
    FILES=$(find . -path "./.git" -prune -o -type f -name "$pattern" -print 2>/dev/null | head -5)
    if [ -n "$FILES" ]; then
        echo ""
        echo "Files matching $pattern:"
        echo "$FILES" | while read -r file; do
            if git ls-files --error-unmatch "$file" &> /dev/null; then
                # File is tracked
                if git-crypt status 2>&1 | grep "$file" | grep -q "encrypted"; then
                    echo "  ✅ $file"
                else
                    echo "  ❌ $file (not encrypted!)"
                    ISSUES=$((ISSUES + 1))
                fi
            fi
        done
    fi
done

echo ""
if [ $ISSUES -eq 0 ]; then
    echo "✅ No issues found"
else
    echo "⚠️  Found $ISSUES potential issue(s)"
    echo ""
    echo "Files that should be encrypted but aren't may need to be re-committed:"
    echo "  git rm --cached <file>"
    echo "  git add <file>"
    echo "  git commit -m 'chore: re-encrypt file'"
fi
echo ""

# Summary
echo "📋 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Encrypted files: $ENCRYPTED_FILES"
echo "Unencrypted files: $UNENCRYPTED_COUNT"
echo "Encryption patterns: $PATTERN_COUNT"
echo "Issues found: $ISSUES"
echo ""

# Test lock/unlock functionality
echo "🧪 Testing lock/unlock:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Test lock/unlock cycle? (yes/no): " test_lock
if [ "$test_lock" = "yes" ]; then
    echo "Locking repository..."
    git-crypt lock 2>&1 || echo "⚠️  Lock failed (may not be unlocked)"
    
    if [ -f "docs/involved_parties.md" ]; then
        if file docs/involved_parties.md 2>/dev/null | grep -q "text"; then
            echo "❌ File still readable (lock didn't work)"
        else
            echo "✅ File is encrypted"
        fi
    fi
    
    echo ""
    echo "⚠️  Repository is now LOCKED"
    echo "To unlock, run:"
    echo "  git-crypt unlock /path/to/key"
    echo ""
    read -p "Unlock now? (yes/no): " unlock_now
    if [ "$unlock_now" = "yes" ]; then
        read -p "Enter path to encryption key: " key_path
        if [ -f "$key_path" ]; then
            git-crypt unlock "$key_path"
            echo "✅ Repository unlocked"
        else
            echo "❌ Key file not found: $key_path"
        fi
    fi
else
    echo "Skipped"
fi
echo ""

# Recommendations
echo "💡 Recommendations:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Verify encryption key is backed up securely"
echo "2. Share key with authorized team members only"
echo "3. Check encryption before committing sensitive data"
echo "4. Verify remote encryption:"
echo "   ./scripts/verify-encryption-remote.sh"
echo "5. Lock repository when stepping away:"
echo "   git-crypt lock"
echo ""

echo "📚 For more information:"
echo "   - docs/GIT_CRYPT_SETUP.md"
echo "   - docs/QUICK_START_ENCRYPTION.md"
echo ""
