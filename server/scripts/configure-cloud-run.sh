#!/bin/bash

# Script to grant Secret Manager access to Cloud Run service account
# Run this after your first deployment to ensure Cloud Run can access secrets

set -e

PROJECT_ID="mitra-348d9"
REGION="us-central1"
SERVICE="mitra-ai-server"

echo "🔧 Configuring Cloud Run service account permissions..."

# Get the Cloud Run service account
CLOUD_RUN_SA=$(gcloud run services describe $SERVICE --region=$REGION --format="value(spec.template.spec.serviceAccountName)" 2>/dev/null || echo "")

if [ -z "$CLOUD_RUN_SA" ]; then
    echo "⚠️  Cloud Run service not found or no custom service account set."
    echo "   Using default Compute Engine service account..."
    CLOUD_RUN_SA="${PROJECT_ID//[^0-9]/}-compute@developer.gserviceaccount.com"
    echo "   Service account: $CLOUD_RUN_SA"
else
    echo "✅ Found Cloud Run service account: $CLOUD_RUN_SA"
fi

# Grant Secret Manager access to the Cloud Run service account
echo "🔐 Granting Secret Manager access..."

# List all secrets with mitra- prefix
SECRETS=$(gcloud secrets list --filter="name:mitra-*" --format="value(name)")

for secret in $SECRETS; do
    echo "   📋 Granting access to secret: $secret"
    gcloud secrets add-iam-policy-binding "$secret" \
        --member="serviceAccount:$CLOUD_RUN_SA" \
        --role="roles/secretmanager.secretAccessor" \
        --quiet
done

echo "✅ Secret Manager permissions configured!"
echo ""
echo "📋 Cloud Run service configuration:"
echo "   Project: $PROJECT_ID"
echo "   Service: $SERVICE"
echo "   Region: $REGION"
echo "   Service Account: $CLOUD_RUN_SA"
echo ""
echo "🚀 Your service should now be able to access all secrets!"