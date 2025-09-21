#!/bin/bash

# Script to set up service account for GitHub Actions CI/CD
# Make sure you're authenticated and have the correct project set:
# gcloud config set project mitra-348d9

set -e

PROJECT_ID="mitra-348d9"
SA_NAME="github-actions"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="github-actions-key.json"

echo "🔧 Setting up GitHub Actions service account for project: $PROJECT_ID"

# Create the service account
echo "📝 Creating service account: $SA_NAME"
if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "   ↪️ Service account already exists"
else
    gcloud iam service-accounts create "$SA_NAME" \
        --display-name="GitHub Actions Deployments" \
        --description="Service account for automated CI/CD deployments from GitHub Actions" \
        --project="$PROJECT_ID"
    echo "   ✅ Service account created"
fi

# Assign required roles
echo "🔐 Assigning IAM roles..."

roles=(
    "roles/run.admin"
    "roles/artifactregistry.writer" 
    "roles/iam.serviceAccountUser"
    "roles/secretmanager.secretAccessor"
    "roles/storage.admin"
)

for role in "${roles[@]}"; do
    echo "   📋 Assigning role: $role"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$role" \
        --quiet
done

# Create and download service account key
echo "🔑 Creating service account key..."
if [ -f "$KEY_FILE" ]; then
    echo "   ⚠️  Key file already exists. Removing old key..."
    rm "$KEY_FILE"
fi

gcloud iam service-accounts keys create "$KEY_FILE" \
    --iam-account="$SA_EMAIL" \
    --project="$PROJECT_ID"

echo "✅ Service account setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Add the service account key to GitHub Secrets:"
echo "   - Go to your GitHub repo → Settings → Secrets and variables → Actions"
echo "   - Create new secret:"
echo "     Name: GCP_SA_KEY"
echo "     Value: (paste the entire contents of $KEY_FILE)"
echo ""
echo "2. Keep the key file secure and DO NOT commit it to git!"
echo "3. The service account email is: $SA_EMAIL"
echo ""
echo "🔍 Service account key location: $(pwd)/$KEY_FILE"