#!/bin/bash
# Verify that files are actually encrypted in the remote repository

set -e

echo "🔍 Verifying Remote Encryption"
echo "==============================="
echo ""

# Create temporary directory
TEMP_DIR=$(mktemp -d)
# Ensure cleanup on exit
trap "rm -rf \"$TEMP_DIR\"" EXIT

echo "📁 Cloning to temporary directory: $TEMP_DIR"

# Get the remote URL dynamically
REMOTE_URL=$(git config --get remote.origin.url 2>/dev/null || echo "https://github.com/stopazus/stop-azs.git")

# Clone repository without unlocking
git clone --quiet "$REMOTE_URL" "$TEMP_DIR/repo"

cd "$TEMP_DIR/repo"

echo ""
echo "🔎 Checking sensitive files..."
echo ""

# Check involved_parties.md
if [ -f "docs/involved_parties.md" ]; then
    # Check for git-crypt magic bytes or specific encrypted markers
    if file "docs/involved_parties.md" | grep -qE "data$|GPG|Git-crypt" || head -c 10 "docs/involved_parties.md" | grep -q "GITCRYPT"; then
        echo "✅ docs/involved_parties.md is ENCRYPTED"
    else
        echo "❌ docs/involved_parties.md is NOT ENCRYPTED"
        echo "   WARNING: Sensitive data may be exposed!"
    fi
fi

# Enable nullglob to handle non-matching patterns gracefully
shopt -s nullglob

# Check other patterns
for pattern in "evidence/*" "case_files/*" "*.sensitive"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            if file "$file" | grep -qE "data$|GPG|Git-crypt" || head -c 10 "$file" | grep -q "GITCRYPT"; then
                echo "✅ $file is ENCRYPTED"
            else
                echo "❌ $file is NOT ENCRYPTED"
            fi
        fi
    done
done

echo ""
echo "✅ Verification complete"
