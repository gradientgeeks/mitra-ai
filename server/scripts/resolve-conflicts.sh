#!/bin/bash

# Script to automatically resolve merge conflicts by taking the feat/voice version
# This script removes conflict markers and keeps the content between =======  and >>>>>>> feat/voice

set -e

echo "🔧 Resolving merge conflicts in Python files..."

# List of files with conflicts
files=(
    "./repository/firestore_repository.py"
    "./models/user.py"
    "./models/chat.py"
    "./services/gemini_service.py"
    "./routers/user.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ] && grep -q "<<<<<<< HEAD" "$file"; then
        echo "📝 Resolving conflicts in: $file"
        
        # Create a backup
        cp "$file" "$file.backup"
        
        # Use sed to remove conflict markers and keep the feat/voice version
        # This removes everything from <<<<<<< HEAD to ======= 
        # and removes >>>>>>> feat/voice markers
        sed -i '/<<<<<<< HEAD/,/=======/d' "$file"
        sed -i '/>>>>>>> feat\/voice/d' "$file"
        
        echo "   ✅ Resolved conflicts in $file"
    else
        echo "   ⚠️  No conflicts found in $file or file doesn't exist"
    fi
done

echo "✅ All merge conflicts resolved!"
echo "📋 You can now commit and push the changes"