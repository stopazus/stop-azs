#!/bin/bash
# Helper script to share git-crypt access with a collaborator

set -e

echo "🔑 Share Git-Crypt Access"
echo "========================="
echo ""

# Check git-crypt installation
if ! command -v git-crypt &> /dev/null; then
    echo "❌ git-crypt is not installed"
    exit 1
fi

# Check if git-crypt is initialized
if ! git-crypt status &> /dev/null 2>&1; then
    echo "❌ git-crypt is not initialized in this repository"
    echo ""
    echo "Initialize first:"
    echo "  ./scripts/setup-git-crypt.sh"
    exit 1
fi

echo "This script helps you share git-crypt access with a collaborator."
echo ""
echo "Choose access method:"
echo "  1) Symmetric key (simpler, share key file)"
echo "  2) GPG key (more secure, no key sharing)"
echo ""
read -p "Choose (1/2): " method

case $method in
  1)
    echo ""
    echo "📤 Sharing via Symmetric Key"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Export key
    read -p "Enter collaborator name (for filename): " collab_name
    KEY_FILE="$HOME/git-crypt-stop-azs-for-${collab_name// /-}.key"
    
    echo "Exporting encryption key..."
    git-crypt export-key "$KEY_FILE"
    
    echo "✅ Key exported to: $KEY_FILE"
    echo ""
    echo "📧 Share this key securely:"
    echo ""
    echo "✅ SECURE methods:"
    echo "  - Password manager (1Password, LastPass, Bitwarden)"
    echo "  - Encrypted email (GPG): gpg --encrypt --recipient email@example.com $KEY_FILE"
    echo "  - Signal/WhatsApp (send as file)"
    echo "  - In-person USB transfer"
    echo ""
    echo "❌ DO NOT use:"
    echo "  - Plain email"
    echo "  - Slack/Teams/Discord"
    echo "  - Public file sharing"
    echo ""
    echo "📋 Instructions for collaborator:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. Install git-crypt:"
    echo "   macOS:   brew install git-crypt"
    echo "   Ubuntu:  sudo apt-get install git-crypt"
    echo ""
    echo "2. Clone repository:"
    echo "   git clone https://github.com/stopazus/stop-azs.git"
    echo "   cd stop-azs"
    echo ""
    echo "3. Unlock with provided key:"
    echo "   git-crypt unlock /path/to/key"
    echo ""
    echo "4. Verify:"
    echo "   git-crypt status"
    echo "   cat docs/involved_parties.md  # Should be readable"
    echo ""
    
    # Offer to copy instructions
    read -p "Copy these instructions to clipboard? (requires xclip/pbcopy) (yes/no): " copy_clip
    if [ "$copy_clip" = "yes" ]; then
        INSTRUCTIONS="Git-Crypt Access Instructions

1. Install git-crypt:
   macOS:   brew install git-crypt
   Ubuntu:  sudo apt-get install git-crypt

2. Clone repository:
   git clone https://github.com/stopazus/stop-azs.git
   cd stop-azs

3. Unlock with provided key:
   git-crypt unlock /path/to/key

4. Verify:
   git-crypt status
   cat docs/involved_parties.md

Encryption key has been shared separately via secure channel."

        if command -v pbcopy &> /dev/null; then
            echo "$INSTRUCTIONS" | pbcopy
            echo "✅ Instructions copied to clipboard (macOS)"
        elif command -v xclip &> /dev/null; then
            echo "$INSTRUCTIONS" | xclip -selection clipboard
            echo "✅ Instructions copied to clipboard (Linux)"
        else
            echo "⚠️  Clipboard tool not found"
            echo "Instructions saved to: /tmp/git-crypt-instructions.txt"
            echo "$INSTRUCTIONS" > /tmp/git-crypt-instructions.txt
        fi
    fi
    ;;
    
  2)
    echo ""
    echo "🔐 Sharing via GPG Key"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Check GPG installation
    if ! command -v gpg &> /dev/null; then
        echo "❌ GPG is not installed"
        echo ""
        echo "Install with:"
        echo "  macOS:   brew install gnupg"
        echo "  Ubuntu:  sudo apt-get install gnupg"
        exit 1
    fi
    
    echo "GPG-based access is more secure:"
    echo "  ✅ No key file to share"
    echo "  ✅ Each user has their own GPG key"
    echo "  ✅ Can revoke access individually"
    echo ""
    echo "📋 Instructions for collaborator:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. Generate GPG key (if don't have one):"
    echo "   gpg --gen-key"
    echo "   # Follow prompts"
    echo ""
    echo "2. Export public key:"
    echo "   gpg --export --armor your-email@example.com > your-name.asc"
    echo ""
    echo "3. Send your-name.asc to repository admin"
    echo "   (This is public, can send via email)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📋 After receiving collaborator's GPG key:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Have you received the collaborator's .asc file? (yes/no): " received
    if [ "$received" = "yes" ]; then
        read -p "Enter path to .asc file: " asc_file
        
        if [ ! -f "$asc_file" ]; then
            echo "❌ File not found: $asc_file"
            exit 1
        fi
        
        echo ""
        echo "Importing GPG key..."
        gpg --import "$asc_file"
        
        echo ""
        echo "List of GPG keys:"
        gpg --list-keys
        
        echo ""
        read -p "Enter collaborator's email address: " collab_email
        
        echo ""
        echo "Adding GPG user to git-crypt..."
        git-crypt add-gpg-user "$collab_email"
        
        echo ""
        echo "Committing changes..."
        git add .git-crypt/
        git commit -m "Add $collab_email to git-crypt" || echo "⚠️  No changes to commit"
        
        echo ""
        read -p "Push changes to remote? (yes/no): " push_now
        if [ "$push_now" = "yes" ]; then
            git push origin "$(git rev-parse --abbrev-ref HEAD)"
            echo "✅ Changes pushed"
        fi
        
        echo ""
        echo "✅ GPG user added!"
        echo ""
        echo "📧 Tell collaborator to:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "1. Pull latest changes:"
        echo "   git pull origin main"
        echo ""
        echo "2. Unlock repository (automatic with GPG):"
        echo "   git-crypt unlock"
        echo "   # Your GPG key will be used automatically"
        echo ""
        echo "3. Verify:"
        echo "   git-crypt status"
        echo ""
    else
        echo ""
        echo "Request the .asc file from collaborator first."
        echo "Then re-run this script."
    fi
    ;;
    
  *)
    echo "❌ Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "📚 For more information:"
echo "   - docs/GIT_CRYPT_SETUP.md"
echo "   - docs/QUICK_START_ENCRYPTION.md"
echo ""
