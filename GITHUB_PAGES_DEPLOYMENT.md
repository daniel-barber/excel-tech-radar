# Deploying Radar Studio to IBM Internal GitHub Pages

This guide walks you through deploying Radar Studio as a static web application to IBM's internal GitHub Pages.

## Overview

GitHub Pages deployment creates a **client-side only** version of Radar Studio that:
- ✅ Runs entirely in the browser (no backend server)
- ✅ Uses local browser storage for data
- ✅ Can be accessed via `https://pages.github.ibm.com/your-org/radar-studio`
- ⚠️ **Note**: This is different from the standalone app - it's a web-only version

## Prerequisites

- [ ] Access to IBM's internal GitHub (github.ibm.com)
- [ ] Repository created or access to existing repo
- [ ] GitHub Pages enabled for your organization
- [ ] Basic knowledge of Git and GitHub

## Architecture Decision

For GitHub Pages, we have two deployment options:

### Option 1: Static Client-Only Version (Recommended for GitHub Pages)
- Pure HTML/CSS/JavaScript
- Data stored in browser LocalStorage
- No backend required
- Perfect for demos and personal use
- **Limitation**: No data persistence across devices

### Option 2: Backend + GitHub Pages (Advanced)
- Frontend on GitHub Pages
- Backend deployed separately (IBM Cloud, Kubernetes, etc.)
- Full features including data persistence
- Requires additional infrastructure

**This guide covers Option 1** (static client-only version).

---

## Step-by-Step Deployment Guide

### Step 1: Prepare Your Repository

#### 1.1 Push Code to IBM GitHub

```bash
# If not already done, initialize git and push to IBM GitHub
cd /path/to/radar-studio

# Add IBM GitHub remote (replace with your actual repo URL)
git remote add origin https://github.ibm.com/your-org/radar-studio.git

# Push code
git add .
git commit -m "Initial commit for GitHub Pages deployment"
git push -u origin main
```

#### 1.2 Verify Repository Structure

Your repository should have:
```
radar-studio/
├── web/                    # Static web files
│   ├── unified.html       # Main HTML file
│   ├── unified.css        # Styles
│   ├── unified.js         # JavaScript
│   ├── favicon.ico        # Icon
│   └── favicon.svg        # Icon
├── .github/
│   └── workflows/
│       └── deploy-pages.yml  # Deployment workflow (we'll create this)
└── README.md
```

---

### Step 2: Create Static Build

Since Radar Studio currently requires a backend, we need to create a client-only version for GitHub Pages.

#### 2.1 Create a Static Build Directory

```bash
mkdir -p docs
```

#### 2.2 Copy Web Files

```bash
# Copy all web assets to docs/ directory
cp web/unified.html docs/index.html
cp web/unified.css docs/style.css
cp web/unified.js docs/app.js
cp web/favicon.ico docs/
cp web/favicon.svg docs/
```

#### 2.3 Modify for Client-Only Mode

The `unified.html` needs to be updated to work without a backend. We'll create a modified version that:
- Uses browser LocalStorage instead of backend API
- Loads sample data or allows file upload
- Removes server-dependent features

---

### Step 3: Create GitHub Actions Workflow

Create `.github/workflows/deploy-pages.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

# Sets permissions for GitHub Pages deployment
permissions:
  contents: read
  pages: write
  id-token: write

# Allow one concurrent deployment
concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Build static site
        run: |
          mkdir -p docs
          cp web/unified.html docs/index.html
          cp web/unified.css docs/style.css
          cp web/unified.js docs/app.js
          cp web/favicon.ico docs/
          cp web/favicon.svg docs/
          
          # Update title in HTML
          sed -i 's|<title>.*</title>|<title>Radar Studio - IBM Internal</title>|g' docs/index.html
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './docs'
  
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

---

### Step 4: Configure Repository Settings

#### 4.1 Enable GitHub Pages

1. Go to your repository on github.ibm.com
2. Click **Settings** tab
3. Scroll to **Pages** section (left sidebar)
4. Under **Source**, select:
   - Source: **GitHub Actions** (recommended)
   - Or: **Deploy from a branch** → select `main` branch and `/docs` folder

#### 4.2 Configure Build Settings

If using "Deploy from a branch":
- Branch: `main`
- Folder: `/docs`

If using "GitHub Actions":
- The workflow will handle deployment automatically

#### 4.3 Save Settings

Click **Save** and wait for deployment to complete.

---

### Step 5: Access Your Deployed Site

After deployment completes (usually 1-2 minutes):

**URL Format**: `https://pages.github.ibm.com/[your-org]/[repo-name]`

Example:
- Organization: `watson-health`
- Repository: `radar-studio`
- URL: `https://pages.github.ibm.com/watson-health/radar-studio`

---

### Step 6: Custom Domain (Optional)

If you want a custom internal domain:

#### 6.1 Add CNAME File

Create `docs/CNAME`:
```
radar-studio.internal.ibm.com
```

#### 6.2 Configure DNS

Work with IBM IT to configure DNS:
- Type: `CNAME`
- Name: `radar-studio.internal.ibm.com`
- Value: `pages.github.ibm.com`

#### 6.3 Update Repository Settings

In GitHub Pages settings:
- Custom domain: `radar-studio.internal.ibm.com`
- Enforce HTTPS: ✅ (recommended)

---

## Client-Only Version Features

### What Works Without Backend

✅ **Visualization**
- Interactive radar display
- Zoom and pan
- Filtering by ring/category
- Search functionality

✅ **Data Input**
- File upload (Excel/JSON)
- Manual entry via forms
- Browser LocalStorage persistence

✅ **Export**
- PNG export (client-side)
- JSON export
- Print functionality

### What Requires Backend (Not Available)

❌ **Server Features**
- Multi-user collaboration
- Centralized data storage
- Automatic backups
- Project management across devices

---

## Deployment Checklist

### Pre-Deployment
- [ ] Code pushed to IBM GitHub
- [ ] Web files tested locally
- [ ] Icons and assets included
- [ ] README updated with deployment URL

### Deployment
- [ ] GitHub Actions workflow created
- [ ] Repository settings configured
- [ ] GitHub Pages enabled
- [ ] Deployment successful

### Post-Deployment
- [ ] Site accessible at GitHub Pages URL
- [ ] All assets loading correctly
- [ ] Functionality tested in browser
- [ ] Documentation updated

---

## Troubleshooting

### Issue: 404 Page Not Found

**Solution**:
- Verify `docs/index.html` exists
- Check GitHub Pages source settings
- Ensure workflow completed successfully

### Issue: Assets Not Loading

**Solution**:
- Check file paths in HTML (use relative paths)
- Verify all files copied to `docs/` directory
- Check browser console for errors

### Issue: Workflow Fails

**Solution**:
- Check workflow logs in Actions tab
- Verify permissions are set correctly
- Ensure branch name matches workflow trigger

### Issue: Site Not Updating

**Solution**:
- Clear browser cache
- Wait 1-2 minutes for deployment
- Check Actions tab for deployment status
- Force refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

---

## Maintenance

### Updating the Site

```bash
# Make changes to web files
nano web/unified.html

# Commit and push
git add .
git commit -m "Update radar visualization"
git push origin main

# GitHub Actions will automatically deploy
```

### Monitoring

- **Actions Tab**: View deployment history and logs
- **Insights > Traffic**: See page views (if enabled)
- **Settings > Pages**: Check deployment status

---

## Security Considerations

### IBM Internal GitHub

✅ **Advantages**:
- Only accessible to IBM employees
- Behind IBM firewall
- SSO authentication
- Audit logging

⚠️ **Considerations**:
- Still accessible to all IBM employees
- Don't store sensitive data in browser
- Use IBM's data classification guidelines
- Consider additional access controls if needed

### Data Privacy

Since this is client-only:
- Data stored in browser LocalStorage
- No server-side storage
- Data doesn't leave user's browser
- Cleared when browser cache is cleared

---

## Alternative: Full-Stack Deployment

If you need backend features, consider:

### Option A: IBM Cloud Foundry
```bash
# Deploy backend to IBM Cloud
cf push radar-studio-api -f manifest.yml

# Update frontend to point to API
# Deploy frontend to GitHub Pages
```

### Option B: IBM Kubernetes (IKS)
```bash
# Deploy as containerized app
kubectl apply -f k8s/deployment.yml

# Expose via IBM Cloud ingress
```

### Option C: IBM Cloud Code Engine
```bash
# Deploy serverless backend
ibmcloud ce application create --name radar-studio
```

---

## Next Steps

After successful deployment:

1. **Share the URL** with your team
2. **Create documentation** for users
3. **Set up monitoring** (if needed)
4. **Plan updates** and maintenance schedule
5. **Gather feedback** from users

---

## Support

For issues specific to:
- **IBM GitHub**: Contact IBM GitHub support
- **GitHub Pages**: Check IBM's internal GitHub Pages documentation
- **Radar Studio**: Open an issue in the repository

---

## Quick Reference

### Useful Commands

```bash
# Test locally before deploying
cd docs && python3 -m http.server 8000

# Force rebuild and deploy
git commit --allow-empty -m "Trigger rebuild"
git push origin main

# Check deployment status
gh workflow view deploy-pages
```

### Useful Links

- IBM GitHub: https://github.ibm.com
- IBM GitHub Pages Docs: [Internal IBM documentation]
- Repository Settings: `https://github.ibm.com/[org]/[repo]/settings/pages`
- Actions: `https://github.ibm.com/[org]/[repo]/actions`

---

**Last Updated**: March 2026  
**Version**: 1.0  
**Maintained By**: Radar Studio Team