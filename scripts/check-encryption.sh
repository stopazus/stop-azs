#!/bin/bash
# Check encryption status of sensitive files

set -e

echo "🔐 Git-Crypt Encryption Status"
echo "=============================="
echo ""

# Check if git-crypt is installed
if ! command -v git-crypt &> /dev/null; then
    echo "❌ git-crypt is not installed"
    echo "   Install: brew install git-crypt (macOS)"
    echo "   Install: sudo apt-get install git-crypt (Linux)"
    exit 1
fi

echo "✅ git-crypt is installed"
echo ""

# Check if repository is initialized
if ! git-crypt status &> /dev/null; then
    echo "⚠️  git-crypt not initialized in this repository"
    echo "   Run: git-crypt init"
    exit 1
fi

echo "✅ git-crypt is initialized"
echo ""

# Show encryption status
echo "📊 Encrypted Files:"
echo "-------------------"
git-crypt status -e

echo ""
echo "📊 All Files Status:"
echo "-------------------"
git-crypt status

echo ""
echo "✅ Check complete"
