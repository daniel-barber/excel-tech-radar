# Release Checklist

Use this checklist when preparing a new release of Excel Tech Radar.

## Pre-Release (1-2 days before)

### Code & Testing
- [ ] All tests passing locally: `pytest tests/ -v`
- [ ] Code formatted: `black src/ tests/`
- [ ] Linting clean: `ruff check src/ tests/`
- [ ] Type checking clean: `mypy src/excel_radar/`
- [ ] No critical security vulnerabilities
- [ ] All GitHub Actions workflows passing

### Version & Documentation
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `README.md` footer
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Review and update `README.md` if needed
- [ ] Review and update `API.md` if API changed
- [ ] Review and update `DEPLOYMENT.md` if deployment changed

### Build Testing
- [ ] Test local build on macOS: `./build/build_mac.sh`
- [ ] Test local build on Windows: `build\build_windows.bat`
- [ ] Verify .app launches on macOS
- [ ] Verify .exe launches on Windows
- [ ] Test directory picker functionality
- [ ] Test server launch and web UI access
- [ ] Test with sample Excel file

## Release Day

### Git Operations
- [ ] Commit all changes: `git commit -am "Release v0.X.X"`
- [ ] Push to main branch: `git push origin main`
- [ ] Create and push tag: 
  ```bash
  git tag v0.X.X
  git push origin v0.X.X
  ```

### Monitor Build
- [ ] Watch GitHub Actions build progress
- [ ] Verify macOS build completes successfully
- [ ] Verify Windows build completes successfully
- [ ] Check for any build warnings or errors

### Download & Test Artifacts
- [ ] Download macOS DMG from GitHub release
- [ ] Download Windows ZIP from GitHub release
- [ ] Test macOS DMG on clean Mac (no Python)
  - [ ] Install from DMG
  - [ ] Launch application
  - [ ] Select data directory
  - [ ] Start server
  - [ ] Access web UI
  - [ ] Load Excel file
  - [ ] Verify visualization
- [ ] Test Windows ZIP on clean Windows (no Python)
  - [ ] Extract ZIP
  - [ ] Run executable
  - [ ] Select data directory
  - [ ] Start server
  - [ ] Access web UI
  - [ ] Load Excel file
  - [ ] Verify visualization

### Release Notes
- [ ] Review auto-generated release notes
- [ ] Edit release notes if needed
- [ ] Add "What's New" section
- [ ] Add "Known Issues" section if applicable
- [ ] Add upgrade instructions if needed
- [ ] Verify download links work

### Documentation
- [ ] Update GitHub repository description
- [ ] Update repository topics/tags
- [ ] Pin release announcement issue
- [ ] Update project website (if applicable)

## Post-Release (within 24 hours)

### Verification
- [ ] Verify release appears on GitHub releases page
- [ ] Verify download links work
- [ ] Check download counts after 24 hours
- [ ] Monitor for user-reported issues

### Communication
- [ ] Announce release (if applicable):
  - [ ] Internal team notification
  - [ ] User mailing list
  - [ ] Social media
  - [ ] Project blog
- [ ] Update any external documentation
- [ ] Update demo/sandbox environment

### Monitoring
- [ ] Check GitHub issues for new bug reports
- [ ] Monitor error logs (if telemetry enabled)
- [ ] Review user feedback
- [ ] Plan hotfix if critical issues found

## Hotfix Process (if needed)

If critical issues are found after release:

1. **Assess Severity**
   - [ ] Determine if hotfix is needed
   - [ ] Document the issue
   - [ ] Estimate impact

2. **Create Hotfix**
   - [ ] Create hotfix branch: `git checkout -b hotfix/v0.X.Y`
   - [ ] Fix the issue
   - [ ] Test thoroughly
   - [ ] Update version to v0.X.Y
   - [ ] Update CHANGELOG.md

3. **Release Hotfix**
   - [ ] Merge to main
   - [ ] Tag: `git tag v0.X.Y`
   - [ ] Push tag: `git push origin v0.X.Y`
   - [ ] Monitor build
   - [ ] Test artifacts
   - [ ] Update release notes

4. **Communicate**
   - [ ] Notify users of hotfix
   - [ ] Explain what was fixed
   - [ ] Provide upgrade instructions

## Version Numbering

Follow Semantic Versioning (semver):

- **Major (X.0.0)**: Breaking changes, major new features
- **Minor (0.X.0)**: New features, backward compatible
- **Patch (0.0.X)**: Bug fixes, backward compatible

Examples:
- `v1.0.0` - First stable release
- `v1.1.0` - Added new feature
- `v1.1.1` - Fixed bug in v1.1.0
- `v2.0.0` - Breaking API changes

## Release Schedule

Recommended release cadence:

- **Major releases**: Every 6-12 months
- **Minor releases**: Every 1-2 months
- **Patch releases**: As needed for critical bugs
- **Security patches**: Immediately when needed

## Rollback Plan

If a release has critical issues:

1. **Immediate Actions**
   - [ ] Mark release as "Pre-release" on GitHub
   - [ ] Add warning to release notes
   - [ ] Pin issue describing the problem

2. **Communication**
   - [ ] Notify users immediately
   - [ ] Provide workaround if available
   - [ ] Estimate fix timeline

3. **Fix & Re-release**
   - [ ] Follow hotfix process above
   - [ ] Test more thoroughly
   - [ ] Release new version

## Automation Checklist

Verify these are working:

- [ ] GitHub Actions build workflow
- [ ] GitHub Actions test workflow
- [ ] Automatic release creation
- [ ] Artifact upload to release
- [ ] Release notes generation

## Security Checklist

Before each release:

- [ ] Review dependencies for vulnerabilities
- [ ] Update dependencies if needed
- [ ] Check for exposed secrets
- [ ] Verify CORS configuration
- [ ] Review authentication/authorization
- [ ] Test with security scanner (if available)

## Performance Checklist

- [ ] Test with large Excel files (1000+ rows)
- [ ] Verify memory usage is reasonable
- [ ] Check startup time
- [ ] Test concurrent users (if applicable)
- [ ] Verify no memory leaks

## Accessibility Checklist

- [ ] Test with screen reader
- [ ] Verify keyboard navigation
- [ ] Check color contrast
- [ ] Test with browser zoom
- [ ] Verify ARIA labels

## Browser Compatibility

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

## Platform Compatibility

Test on:
- [ ] macOS 10.13+
- [ ] macOS 11+ (Apple Silicon)
- [ ] Windows 10
- [ ] Windows 11

## Notes

- Keep this checklist updated as process evolves
- Add items based on lessons learned
- Remove items that are automated
- Share feedback with team

## Emergency Contacts

In case of critical issues:

- **Lead Developer**: [Name/Email]
- **DevOps**: [Name/Email]
- **Security**: [Name/Email]

## Resources

- [GitHub Releases](https://github.com/yourusername/excel-tech-radar/releases)
- [GitHub Actions](https://github.com/yourusername/excel-tech-radar/actions)
- [PACKAGING.md](./PACKAGING.md)
- [CHANGELOG.md](./CHANGELOG.md)