#!/bin/bash
# Verify that files are actually encrypted in the remote repository

set -e

echo "🔍 Verifying Remote Encryption"
echo "==============================="
echo ""

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "📁 Cloning to temporary directory: $TEMP_DIR"

# Clone repository without unlocking
git clone https://github.com/stopazus/stop-azs.git "$TEMP_DIR/repo" 2>&1 | grep -v "Cloning"

cd "$TEMP_DIR/repo"

echo ""
echo "🔎 Checking sensitive files..."
echo ""

# Check involved_parties.md
if [ -f "docs/involved_parties.md" ]; then
    if file "docs/involved_parties.md" | grep -q "data\|GPG\|encrypted"; then
        echo "✅ docs/involved_parties.md is ENCRYPTED"
    else
        echo "❌ docs/involved_parties.md is NOT ENCRYPTED"
        echo "   WARNING: Sensitive data may be exposed!"
    fi
fi

# Check other patterns
for pattern in "evidence/*" "case_files/*" "*.sensitive"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            if file "$file" | grep -q "data\|GPG\|encrypted"; then
                echo "✅ $file is ENCRYPTED"
            else
                echo "❌ $file is NOT ENCRYPTED"
            fi
        fi
    done
done

# Cleanup
cd ../..
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Verification complete"
