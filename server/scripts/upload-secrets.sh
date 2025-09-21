#!/bin/bash

# Script to upload environment variables to Google Cloud Secret Manager
# Make sure you're authenticated and have the correct project set:
# gcloud config set project mitra-348d9

set -e

PROJECT_ID="mitra-348d9"
ENV_FILE=".env"

echo "🔐 Uploading secrets to Google Cloud Secret Manager for project: $PROJECT_ID"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

# Function to create or update a secret
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2
    
    echo "📝 Processing secret: $secret_name"
    
    # Check if secret exists
    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" >/dev/null 2>&1; then
        echo "   ↪️ Secret exists, adding new version..."
        echo -n "$secret_value" | gcloud secrets versions add "$secret_name" --data-file=-
    else
        echo "   ➕ Creating new secret..."
        echo -n "$secret_value" | gcloud secrets create "$secret_name" --replication-policy="automatic" --data-file=-
    fi
}

# Read .env file and process each non-comment line
while IFS= read -r line; do
    # Skip empty lines and comments
    if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Extract key and value
    if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"
        
        # Skip if value is empty
        if [[ -z "$value" ]]; then
            echo "⚠️  Skipping empty value for: $key"
            continue
        fi
        
        # Add MITRA_ prefix and convert to lowercase with hyphens for Secret Manager naming
        secret_name="mitra-$(echo "$key" | tr '[:upper:]' '[:lower:]' | tr '_' '-')"
        
        create_or_update_secret "$secret_name" "$value"
    fi
done < "$ENV_FILE"

# Also upload the Firebase service account JSON as a secret
if [ -f "mitra-348d9-firebase-adminsdk-fbsvc-f582a66e18.json" ]; then
    echo "📝 Processing Firebase service account JSON..."
    create_or_update_secret "mitra-firebase-service-account-key" "$(cat mitra-348d9-firebase-adminsdk-fbsvc-f582a66e18.json)"
fi

echo "✅ All secrets uploaded successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Grant Secret Manager access to your Cloud Run service account:"
echo "   gcloud projects add-iam-policy-binding $PROJECT_ID \\"
echo "     --member=\"serviceAccount:YOUR_CLOUD_RUN_SERVICE_ACCOUNT\" \\"
echo "     --role=\"roles/secretmanager.secretAccessor\""
echo ""
echo "2. Create a service account for GitHub Actions deployment"
echo "3. Set up GitHub Actions workflow"