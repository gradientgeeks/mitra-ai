# Mitra AI - Production CI/CD Setup Guide

## Overview
This guide sets up a complete production-grade CI/CD pipeline for Mitra AI using Google Cloud Run, Secret Manager, and GitHub Actions.

## Architecture
- **FastAPI Application**: Containerized with Docker
- **Google Cloud Run**: Serverless deployment platform
- **Google Secret Manager**: Secure secrets storage
- **GitHub Actions**: Automated CI/CD pipeline
- **Google Container Registry**: Docker image storage

## Setup Steps

### 1. ✅ Secrets Management
All environment variables have been uploaded to Google Cloud Secret Manager with MITRA_ prefix:
- `mitra-google-api-key`
- `mitra-firebase-project-id`
- `mitra-firebase-storage-bucket`
- `mitra-firebase-service-account-key`
- And all other configuration variables...

### 2. ✅ Service Account Setup
GitHub Actions service account created with required permissions:
- Service Account: `github-actions@mitra-348d9.iam.gserviceaccount.com`
- Key file: `github-actions-key.json` (DO NOT COMMIT TO GIT!)

### 3. ✅ GitHub Repository Configuration
**IMPORTANT**: Add the service account key to GitHub Secrets:

1. Go to your GitHub repo: https://github.com/Uttam-Mahata/mitra-ai
2. Navigate to: **Settings → Secrets and variables → Actions**
3. Click **New repository secret**
4. Name: `GCP_SA_KEY`
5. Value: Copy and paste the entire contents of `github-actions-key.json`

### 4. ✅ Docker Configuration
- Production-ready `Dockerfile` created
- `.dockerignore` configured to exclude sensitive files
- Health checks and security best practices implemented

### 5. ✅ GitHub Actions Workflow
- File: `.github/workflows/deploy.yml`
- Triggers on push to `main` and `feat/voice` branches
- Runs tests on pull requests
- Builds and deploys to Cloud Run automatically

### 6. 🔄 Initial Deployment

To trigger your first deployment:

```bash
# Make sure you're on the right branch
git checkout feat/voice

# Add all the new files
git add .

# Commit the changes
git commit -m "feat: add production CI/CD pipeline with Cloud Run deployment"

# Push to trigger deployment
git push origin feat/voice
```

The GitHub Actions workflow will:
1. Build the Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Test the deployment

### 7. 🔧 Post-Deployment Configuration

After the first successful deployment, run:

```bash
cd server
./scripts/configure-cloud-run.sh
```

This ensures Cloud Run can access all secrets from Secret Manager.

## 🔗 Service URLs

After deployment, your service will be available at:
- **Production**: `https://mitra-ai-server-us-central1-xxxxx.a.run.app`
- **Health Check**: `https://mitra-ai-server-us-central1-xxxxx.a.run.app/health`
- **API Docs**: `https://mitra-ai-server-us-central1-xxxxx.a.run.app/docs`

## 🏗️ Infrastructure Details

### Cloud Run Configuration
- **Memory**: 2GB
- **CPU**: 1 vCPU
- **Max Instances**: 10
- **Min Instances**: 0 (scales to zero)
- **Timeout**: 3600 seconds
- **Concurrency**: 80 requests per instance

### Security Features
- Non-root user in container
- Secrets managed via Secret Manager
- Service account with minimal required permissions
- HTTPS-only access
- Vulnerability scanning enabled

### Monitoring & Logging
- Health checks every 30 seconds
- Automatic logging to Google Cloud Logging
- Deployment status notifications
- Image cleanup (keeps 5 most recent versions)

## 🛠️ Available Scripts

### Development Scripts
- `./scripts/upload-secrets.sh` - Upload environment variables to Secret Manager
- `./scripts/setup-github-actions-sa.sh` - Set up GitHub Actions service account
- `./scripts/configure-cloud-run.sh` - Configure Cloud Run permissions

### Manual Deployment (if needed)
```bash
# Build and push manually
cd server
docker build -t gcr.io/mitra-348d9/mitra-ai-server:manual .
docker push gcr.io/mitra-348d9/mitra-ai-server:manual

# Deploy manually
gcloud run deploy mitra-ai-server \
  --image gcr.io/mitra-348d9/mitra-ai-server:manual \
  --region us-central1 \
  --platform managed
```

## 🔍 Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure service account has correct roles
2. **Secrets Not Found**: Verify secret names match in Secret Manager
3. **Build Failures**: Check Dockerfile and requirements.txt
4. **Health Check Failed**: Ensure `/health` endpoint works locally

### Useful Commands
```bash
# Check service status
gcloud run services describe mitra-ai-server --region=us-central1

# View logs
gcloud logs read --service=mitra-ai-server --region=us-central1

# List secrets
gcloud secrets list --filter="name:mitra-*"

# Test locally
cd server
docker build -t mitra-ai-local .
docker run -p 8080:8080 --env-file .env mitra-ai-local
```

## 🚀 Next Steps

1. **Monitoring**: Set up Google Cloud Monitoring alerts
2. **Custom Domain**: Configure custom domain for production
3. **Environment Separation**: Set up staging environment
4. **Database**: Configure Cloud SQL or Firestore for production data
5. **CDN**: Set up Cloud CDN for static assets
6. **Backup**: Configure automated backups

## 🔐 Security Checklist

- ✅ Secrets stored in Secret Manager (not in code)
- ✅ Service accounts with minimal permissions
- ✅ Private container registry
- ✅ HTTPS-only traffic
- ✅ Sensitive files excluded from builds
- ✅ Non-root container user
- ✅ Health checks configured
- ✅ Automatic security updates

Your Mitra AI application is now ready for production! 🎉