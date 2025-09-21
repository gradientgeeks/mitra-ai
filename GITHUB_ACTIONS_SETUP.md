# GitHub Actions Setup for CI/CD

## Why the workflow might not be triggering:

### 1. **Missing GitHub Secret** ⚠️
The most likely reason is that the `GCP_SA_KEY` secret is not configured in the GitHub repository.

**To fix this:**
1. Go to https://github.com/gradientgeeks/mitra-ai/settings/secrets/actions
2. Click **"New repository secret"**
3. Name: `GCP_SA_KEY`
4. Value: Copy the entire contents of the file `/home/uttam/mitra-ai/server/github-actions-key.json`

### 2. **Repository Permissions** 🔐
Make sure you have admin access to `gradientgeeks/mitra-ai` to:
- Enable GitHub Actions (if disabled)
- Add repository secrets
- View workflow runs

### 3. **Workflow Triggers** 🚀
The workflow triggers on:
- Push to `master`, `main`, or `feat/voice` branches
- Changes in `server/**` or `.github/workflows/**` paths
- Manual trigger (workflow_dispatch)

### 4. **Manual Trigger** 🔄
You can now manually trigger the workflow:
1. Go to https://github.com/gradientgeeks/mitra-ai/actions
2. Select "Build and Deploy Mitra AI to Cloud Run"
3. Click "Run workflow"

## Check Workflow Status:
Visit: https://github.com/gradientgeeks/mitra-ai/actions

## Next Steps:
1. ✅ Add the `GCP_SA_KEY` secret (most important!)
2. ✅ Test with a manual trigger
3. ✅ Verify the deployment works
4. ✅ Remove the test file: `rm server/test_trigger.txt`

## Service Account Key Location:
```bash
cat /home/uttam/mitra-ai/server/github-actions-key.json
```

Copy this entire JSON content to the GitHub secret.