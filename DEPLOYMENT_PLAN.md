# GitHub Pages Deployment Plan for Radar Studio

## Quick Start Summary

To deploy Radar Studio to IBM's internal GitHub Pages, you'll need to:

1. ✅ **Read the full guide**: `GITHUB_PAGES_DEPLOYMENT.md`
2. 📝 **Create workflow file**: `.github/workflows/deploy-pages.yml` (see below)
3. 📁 **Prepare static files**: Copy web files to `docs/` directory
4. ⚙️ **Configure GitHub**: Enable Pages in repository settings
5. 🚀 **Deploy**: Push to main branch or trigger workflow manually

---

## Files to Create

### 1. GitHub Actions Workflow

**File**: `.github/workflows/deploy-pages.yml`

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:  # Allow manual trigger

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
    name: Build Static Site
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Build static site
        run: |
          echo "Building static site for GitHub Pages..."
          
          # Create docs directory
          mkdir -p docs
          
          # Copy web files
          cp web/unified.html docs/index.html
          cp web/unified.css docs/style.css
          cp web/unified.js docs/app.js
          cp web/favicon.ico docs/
          cp web/favicon.svg docs/
          
          # Update title for IBM internal deployment
          sed -i 's|<title>Radar Studio</title>|<title>Radar Studio - IBM Internal</title>|g' docs/index.html
          
          # Add IBM branding comment
          echo "<!-- Deployed to IBM Internal GitHub Pages -->" >> docs/index.html
          
          echo "✓ Static site built successfully"
          ls -la docs/
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './docs'
  
  deploy:
    name: Deploy to Pages
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
      
      - name: Output deployment URL
        run: |
          echo "🚀 Deployed to: ${{ steps.deployment.outputs.page_url }}"
```

**To create this file**:
```bash
mkdir -p .github/workflows
nano .github/workflows/deploy-pages.yml
# Paste the content above
```

---

### 2. Static Build Script (Optional)

**File**: `build/build_static.sh`

```bash
#!/bin/bash
# Build static version for GitHub Pages deployment

set -e

echo "======================================"
echo "Radar Studio - Static Build for Pages"
echo "======================================"
echo ""

# Clean and create docs directory
rm -rf docs
mkdir -p docs

# Copy web files
echo "Copying web files..."
cp web/unified.html docs/index.html
cp web/unified.css docs/style.css
cp web/unified.js docs/app.js
cp web/favicon.ico docs/
cp web/favicon.svg docs/

# Update title
echo "Updating page title..."
sed -i '' 's|<title>Radar Studio</title>|<title>Radar Studio - IBM Internal</title>|g' docs/index.html

# Create .nojekyll file (tells GitHub Pages not to use Jekyll)
touch docs/.nojekyll

# Create README for docs directory
cat > docs/README.md << 'EOF'
# Radar Studio - Static Build

This directory contains the static build for GitHub Pages deployment.

**Do not edit files here directly** - they are generated from `web/` directory.

To rebuild:
```bash
./build/build_static.sh
```
EOF

echo ""
echo "✓ Static build complete!"
echo "Files created in docs/ directory:"
ls -la docs/

echo ""
echo "Next steps:"
echo "1. Test locally: cd docs && python3 -m http.server 8000"
echo "2. Commit: git add docs && git commit -m 'Build static site'"
echo "3. Push: git push origin main"
```

**To create and use**:
```bash
nano build/build_static.sh
chmod +x build/build_static.sh
./build/build_static.sh
```

---

### 3. CNAME File (For Custom Domain)

**File**: `docs/CNAME`

```
radar-studio.internal.ibm.com
```

**Only create if you have a custom domain configured with IBM IT.**

---

## Step-by-Step Execution Plan

### Phase 1: Preparation (5 minutes)

```bash
# 1. Ensure you're on main branch
git checkout main
git pull origin main

# 2. Create workflow file
mkdir -p .github/workflows
nano .github/workflows/deploy-pages.yml
# Paste workflow content from above

# 3. Create build script (optional)
nano build/build_static.sh
chmod +x build/build_static.sh

# 4. Build static site
./build/build_static.sh
# OR manually:
mkdir -p docs
cp web/unified.html docs/index.html
cp web/unified.css docs/style.css
cp web/unified.js docs/app.js
cp web/favicon.ico docs/
cp web/favicon.svg docs/

# 5. Test locally
cd docs
python3 -m http.server 8000
# Open http://localhost:8000 in browser
# Verify everything works
cd ..
```

### Phase 2: Commit and Push (2 minutes)

```bash
# 1. Add files
git add .github/workflows/deploy-pages.yml
git add docs/
git add build/build_static.sh  # if created

# 2. Commit
git commit -m "Add GitHub Pages deployment workflow and static build"

# 3. Push to IBM GitHub
git push origin main
```

### Phase 3: Configure GitHub Pages (3 minutes)

1. **Go to repository on github.ibm.com**
   - Navigate to: `https://github.ibm.com/[your-org]/[repo-name]`

2. **Open Settings**
   - Click **Settings** tab at top

3. **Navigate to Pages**
   - Click **Pages** in left sidebar

4. **Configure Source**
   - **Source**: Select "GitHub Actions"
   - Click **Save**

5. **Wait for deployment**
   - Go to **Actions** tab
   - Watch "Deploy to GitHub Pages" workflow
   - Should complete in 1-2 minutes

### Phase 4: Verify Deployment (2 minutes)

1. **Get deployment URL**
   - In Actions tab, click on completed workflow
   - Look for deployment URL in logs
   - Format: `https://pages.github.ibm.com/[org]/[repo]`

2. **Test the site**
   - Open URL in browser
   - Verify radar loads correctly
   - Test functionality
   - Check all assets load (icons, CSS, JS)

3. **Share with team**
   - Add URL to README.md
   - Share in team chat
   - Add to documentation

---

## Troubleshooting Guide

### Problem: Workflow fails with "Permission denied"

**Solution**:
```bash
# Check repository settings
# Settings > Actions > General > Workflow permissions
# Select: "Read and write permissions"
# Check: "Allow GitHub Actions to create and approve pull requests"
```

### Problem: 404 Page Not Found

**Solution**:
```bash
# Verify docs/index.html exists
ls -la docs/

# Check GitHub Pages settings
# Settings > Pages > Source should be "GitHub Actions"

# Force rebuild
git commit --allow-empty -m "Trigger rebuild"
git push origin main
```

### Problem: Assets not loading (CSS/JS)

**Solution**:
```bash
# Check file paths in docs/index.html
# Should use relative paths:
# <link rel="stylesheet" href="style.css">
# <script src="app.js"></script>

# NOT absolute paths like:
# <link rel="stylesheet" href="/style.css">
```

### Problem: Site works locally but not on GitHub Pages

**Solution**:
```bash
# Check browser console for errors
# Common issues:
# 1. Mixed content (HTTP vs HTTPS)
# 2. Absolute paths instead of relative
# 3. Missing files

# Test with base path:
# Open: http://localhost:8000/index.html
# Not: http://localhost:8000/
```

---

## Post-Deployment Checklist

- [ ] Site accessible at GitHub Pages URL
- [ ] All pages load correctly
- [ ] Icons and favicon display
- [ ] CSS styling applied
- [ ] JavaScript functionality works
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Tested in multiple browsers
- [ ] URL added to README
- [ ] Team notified
- [ ] Documentation updated

---

## Maintenance Plan

### Regular Updates

```bash
# 1. Make changes to web files
nano web/unified.html

# 2. Rebuild static site
./build/build_static.sh

# 3. Test locally
cd docs && python3 -m http.server 8000

# 4. Commit and push
git add docs/
git commit -m "Update radar visualization"
git push origin main

# 5. Verify deployment
# Check Actions tab for successful deployment
```

### Monitoring

- **Weekly**: Check site is accessible
- **Monthly**: Review analytics (if enabled)
- **Quarterly**: Update dependencies
- **Annually**: Review and update documentation

---

## Alternative Deployment Options

If GitHub Pages doesn't meet your needs:

### Option A: IBM Cloud Static Website

```bash
# Deploy to IBM Cloud Object Storage
ibmcloud cos upload --bucket radar-studio --key index.html --file docs/index.html
```

### Option B: IBM Cloud Foundry

```bash
# Deploy as static app
cf push radar-studio -b staticfile_buildpack
```

### Option C: Internal Web Server

```bash
# Copy to internal web server
scp -r docs/* user@internal-server:/var/www/radar-studio/
```

---

## Security Considerations

### IBM Internal Deployment

✅ **Secure by default**:
- Behind IBM firewall
- Requires IBM SSO
- Audit logging enabled
- Only accessible to IBM employees

⚠️ **Additional considerations**:
- Don't commit sensitive data
- Use IBM data classification
- Follow IBM security policies
- Consider additional access controls

### Data Handling

Since this is client-only:
- Data stored in browser LocalStorage
- No server-side storage
- Data doesn't leave user's browser
- Follows IBM data residency requirements

---

## Success Metrics

Track these metrics post-deployment:

- **Accessibility**: Site uptime and availability
- **Performance**: Page load times
- **Usage**: Number of users/sessions
- **Feedback**: User satisfaction scores
- **Issues**: Bug reports and resolution time

---

## Next Steps After Deployment

1. **Create user documentation**
   - How to access the site
   - How to use features
   - FAQ section

2. **Set up monitoring**
   - Uptime monitoring
   - Error tracking
   - Usage analytics

3. **Plan updates**
   - Feature roadmap
   - Bug fix schedule
   - Maintenance windows

4. **Gather feedback**
   - User surveys
   - Feature requests
   - Bug reports

5. **Scale if needed**
   - Consider backend deployment
   - Evaluate performance
   - Plan for growth

---

## Quick Reference Commands

```bash
# Build static site
./build/build_static.sh

# Test locally
cd docs && python3 -m http.server 8000

# Deploy
git add docs/ && git commit -m "Update site" && git push

# Force rebuild
git commit --allow-empty -m "Rebuild" && git push

# Check deployment status
# Visit: https://github.ibm.com/[org]/[repo]/actions
```

---

## Support Contacts

- **GitHub Issues**: Repository issues tab
- **IBM GitHub Support**: [Internal support channel]
- **Team Lead**: [Your team lead]
- **Documentation**: This file and GITHUB_PAGES_DEPLOYMENT.md

---

**Ready to deploy?** Follow the steps above and you'll have Radar Studio running on IBM's internal GitHub Pages in about 15 minutes!

Good luck! 🚀