# 🚀 GitHub → Jenkins CI/CD Automation Setup

## ⚙️ **Step 1: Get Your Jenkins URL**

### If Jenkins is running locally:
```bash
# Start Jenkins (if using Docker)
docker run -d -p 8080:8080 --name jenkins jenkins/jenkins:latest

# OR if installed locally
# Jenkins typically runs on: http://localhost:8080
```

### If Jenkins is on a remote server:
- Get the server IP/domain
- Example: `http://your-server.com:8080`

---

## 🔧 **Step 2: Install Jenkins Plugins**

1. Go to: `http://YOUR_JENKINS_URL/manage` (Jenkins URL dashboard)
2. Click **Plugin Manager** 
3. Search and install:
   - ✅ **GitHub plugin**
   - ✅ **Pipeline plugin**
   - ✅ **Docker plugin**
   - ✅ **CloudBees Docker Build and Publish**
   - ✅ **Azure Credentials** (for Azure integration)

4. **Restart Jenkins** after installing

---

## 📌 **Step 3: Create a Jenkins Pipeline Job**

1. Jenkins Dashboard → **+ New Item**
2. Enter Job Name: `flask-app-pipeline`
3. Select: **Pipeline**
4. Click **OK**

### Configure the Job:

**Build Triggers:**
- ✅ Check: **GitHub hook trigger for GITScm polling**

**Pipeline:**
- Select: **Pipeline script from SCM**
- SCM: **Git**
- Repository URL: `https://github.com/YOUR_USERNAME/flask-mysql-app.git`
- Credentials: Add your GitHub credentials (if private repo)
- Branch: `*/main`
- Script Path: `Jenkinsfile`

5. Click **Save**

---

## 🔗 **Step 4: Create GitHub Webhook**

1. Go to your GitHub repo: `https://github.com/YOUR_USERNAME/flask-mysql-app`
2. Click **Settings** → **Webhooks** → **Add webhook**

Fill in:
```
Payload URL:        http://YOUR_JENKINS_URL/github-webhook/
Content type:       application/json
Events:             Just the push event ✓
Active:             ✓ Checked
```

⚠️ **IMPORTANT - Network Accessibility:**
- If Jenkins is **localhost**, GitHub can't reach it
- Solution for localhost testing:
  - Use ngrok: `ngrok http 8080` → Copy URL
  - Use that URL in webhook

Example with ngrok:
```
Payload URL: https://abc123.ngrok.io/github-webhook/
```

3. Click **Add webhook**

---

## ✅ **Step 5: Test the Automation**

### Test locally:
```bash
cd /Users/dhanashree/flask-mysql-app

# Make a change
echo "# Test comment" >> app.py

# Commit and push
git add .
git commit -m "test: trigger jenkins pipeline"
git push origin main
```

### Monitor Jenkins:
1. Go to: `http://YOUR_JENKINS_URL/job/flask-app-pipeline/`
2. Watch the **Build History**
3. Click on the latest build → **Console Output**

---

## 🛠️ **Troubleshooting**

### Webhook not triggering?

**Check webhook delivery:**
1. GitHub repo → Settings → Webhooks
2. Click your webhook → **Recent Deliveries**
3. If red ❌: Check the error

**Common issues:**
```bash
# Issue: "Connection refused"
→ Jenkins not accessible from internet
→ Use ngrok or make Jenkins public

# Issue: "404 Not Found"  
→ Jenkins path is wrong
→ Should be: /github-webhook/

# Issue: Webhook created but no builds
→ Job not configured for GitHub trigger
→ Re-check "GitHub hook trigger for GITScm polling"
```

---

## 🔐 **Step 6: Configure Azure Container Registry (Optional)**

For pushing to Azure:

1. Get Azure credentials:
```bash
az acr credential show --name your-registry-name
```

2. In Jenkins: 
   - Manage Jenkins → Manage Credentials
   - Add new credentials (Username + Password)
   - Use in Jenkinsfile

3. Update Jenkinsfile with your registry:
```groovy
DOCKER_REGISTRY = "your-registry.azurecr.io"
```

---

## 📊 **Your Pipeline Stages:**

```
✓ Checkout (from GitHub)
✓ Validate (check required files)
✓ Security Scan (Dockerfile with Hadolint)
✓ Build Docker Image
✓ Container Scan (Vulnerabilities with Trivy)
✓ Unit Tests (pytest)
✓ Deploy to Dev (run container)
✓ Smoke Tests (health check)
✓ Push to Registry (Azure Container Registry)
```

---

## 📝 **Next Steps for Option 2:**

- [ ] Install Hadolint: `brew install hadolint`
- [ ] Install Trivy: `brew install trivy`
- [ ] Set up Azure Container Registry
- [ ] Create staging/production deployment stages
- [ ] Add Slack notifications
- [ ] Create multi-branch pipeline

---

## 🎯 **You're automating:**

✅ Code push → Automatic tests & scans
✅ Security checks before deployment  
✅ Docker image builds in parallel
✅ Deployed to dev automatically
✅ Container scanned for vulnerabilities
✅ All logged & auditable

This is **true DevOps automation!** 🚀

