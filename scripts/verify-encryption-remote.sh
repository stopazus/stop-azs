#!/bin/bash
# Verify that encrypted files are actually encrypted on GitHub

set -e

echo "🌐 Verify Remote Encryption on GitHub"
echo "======================================="
echo ""

# Check requirements
if ! command -v git &> /dev/null; then
    echo "❌ git is not installed"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    echo "❌ curl is not installed"
    exit 1
fi

# Get repository info
REPO_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$REPO_URL" ]; then
    echo "❌ No git remote 'origin' found"
    exit 1
fi

echo "Repository: $REPO_URL"
echo ""

# Extract owner and repo from URL
if [[ $REPO_URL =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
    OWNER="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]}"
else
    echo "❌ Could not parse GitHub repository from URL"
    exit 1
fi

echo "Owner: $OWNER"
echo "Repo: $REPO"
echo ""

# Get current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Branch: $BRANCH"
echo ""

# List of files to check (known encrypted files from .gitattributes)
ENCRYPTED_FILES=(
    "docs/involved_parties.md"
    ".env.production"
    ".env.staging"
)

echo "🔍 Checking encryption status on GitHub..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CHECKED=0
ENCRYPTED=0
UNENCRYPTED=0
NOT_FOUND=0

for file in "${ENCRYPTED_FILES[@]}"; do
    echo -n "Checking: $file ... "
    
    # Construct GitHub raw URL
    RAW_URL="https://raw.githubusercontent.com/$OWNER/$REPO/$BRANCH/$file"
    
    # Try to fetch the file
    RESPONSE=$(curl -s -w "\n%{http_code}" "$RAW_URL" 2>/dev/null || echo "000")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    CONTENT=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "404" ]; then
        echo "❓ Not found"
        NOT_FOUND=$((NOT_FOUND + 1))
    elif [ "$HTTP_CODE" = "200" ]; then
        # Check if content appears to be binary/encrypted
        # Git-crypt encrypted files start with binary data
        if echo "$CONTENT" | head -c 100 | grep -q "GITCRYPT" 2>/dev/null; then
            echo "✅ Encrypted (GITCRYPT header found)"
            ENCRYPTED=$((ENCRYPTED + 1))
        elif file <(echo "$CONTENT") 2>/dev/null | grep -q "data"; then
            echo "✅ Encrypted (binary data)"
            ENCRYPTED=$((ENCRYPTED + 1))
        elif echo "$CONTENT" | head -c 20 | LC_ALL=C grep -q '[^[:print:][:space:]]'; then
            echo "✅ Encrypted (non-printable bytes)"
            ENCRYPTED=$((ENCRYPTED + 1))
        else
            echo "❌ UNENCRYPTED (readable text!)"
            UNENCRYPTED=$((UNENCRYPTED + 1))
            echo "   Preview: $(echo "$CONTENT" | head -c 100 | tr -d '\n')..."
        fi
    else
        echo "⚠️  HTTP $HTTP_CODE"
    fi
    
    CHECKED=$((CHECKED + 1))
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Results:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Files checked: $CHECKED"
echo "✅ Encrypted: $ENCRYPTED"
echo "❌ Unencrypted: $UNENCRYPTED"
echo "❓ Not found: $NOT_FOUND"
echo ""

# Additional check: Verify files that SHOULD exist based on patterns
echo "🔍 Checking for sensitive file patterns..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for .pem, .key files in repository
SENSITIVE_PATTERNS=("*.pem" "*.key" "*.env.production" "secrets/*")

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    FILES=$(git ls-files "$pattern" 2>/dev/null || echo "")
    if [ -n "$FILES" ]; then
        echo ""
        echo "Files matching '$pattern':"
        echo "$FILES" | while read -r file; do
            if [ -n "$file" ]; then
                # Try to fetch from GitHub
                RAW_URL="https://raw.githubusercontent.com/$OWNER/$REPO/$BRANCH/$file"
                HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$RAW_URL" 2>/dev/null || echo "000")
                
                if [ "$HTTP_CODE" = "200" ]; then
                    CONTENT=$(curl -s "$RAW_URL" 2>/dev/null || echo "")
                    if echo "$CONTENT" | head -c 20 | LC_ALL=C grep -q '[^[:print:][:space:]]'; then
                        echo "  ✅ $file (encrypted)"
                    else
                        echo "  ❌ $file (UNENCRYPTED!)"
                    fi
                else
                    echo "  ❓ $file (HTTP $HTTP_CODE)"
                fi
            fi
        done
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $UNENCRYPTED -gt 0 ]; then
    echo ""
    echo "⚠️  WARNING: Found unencrypted sensitive files on GitHub!"
    echo ""
    echo "Action required:"
    echo "1. Verify these files match .gitattributes patterns"
    echo "2. Re-commit to trigger encryption:"
    echo "   git rm --cached <file>"
    echo "   git add <file>"
    echo "   git commit -m 'chore: re-encrypt file'"
    echo "   git push"
    echo ""
    echo "3. If files contain secrets, rotate them immediately"
    echo "   (assume they are compromised)"
    echo ""
    exit 1
elif [ $ENCRYPTED -eq 0 ] && [ $NOT_FOUND -gt 0 ]; then
    echo ""
    echo "ℹ️  No encrypted files found on GitHub yet"
    echo "This is normal if you haven't committed sensitive files yet."
    echo ""
else
    echo ""
    echo "✅ All checked files are properly encrypted on GitHub!"
    echo ""
fi

echo "📚 For more information:"
echo "   - docs/GIT_CRYPT_SETUP.md"
echo "   - ./scripts/check-encryption.sh (local check)"
echo ""
