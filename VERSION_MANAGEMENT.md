# Version Management Guide

## Current Version System

This project uses **Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`

- **MAJOR** (0.x.x): Breaking changes, incompatible API changes
- **MINOR** (x.1.x): New features, backwards-compatible  
- **PATCH** (x.x.1): Bug fixes, backwards-compatible

Current version: **0.1.0**
- `0` = Pre-release/beta (not production-ready)
- `1` = First minor version
- `0` = No patches yet

## Version Location

The version number is stored in **ONE place only**:

**`pyproject.toml`** (line 7):
```toml
version = "0.1.0"
```

All other files automatically read from this single source of truth:
- `src/excel_radar/version.py` - Reads from pyproject.toml at runtime
- `excel-radar.spec` - Reads from pyproject.toml during build
- Build scripts - Read from pyproject.toml

## When to Increment

### PATCH (0.1.0 → 0.1.1)
Increment for:
- Bug fixes
- Performance improvements
- Documentation updates
- Minor UI tweaks
- Security patches

**Example:** Fixing the propensity color bug, improving error messages

### MINOR (0.1.0 → 0.2.0)
Increment for:
- New features
- New functionality
- Backwards-compatible changes
- Significant improvements

**Example:** Adding new visualization types, new export formats

### MAJOR (0.1.0 → 1.0.0)
Increment for:
- Breaking changes
- API changes that break compatibility
- Major redesigns
- Production-ready release (0.x.x → 1.0.0)

**Example:** Changing config file format, removing deprecated features

## How to Update Version

### Manual Method (Recommended for now)

1. **Decide what to increment** based on your changes

2. **Update version in ONE place** - `pyproject.toml`:
   ```toml
   version = "0.1.1"  # or 0.2.0, or 1.0.0
   ```
   
   That's it! All other files read from this automatically.

3. **Commit the version bump**:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.1.1"
   ```

4. **Tag the release**:
   ```bash
   git tag -a v0.1.1 -m "Release v0.1.1"
   git push origin v0.1.1
   ```

### Using the Bump Script (Coming Soon)

A `scripts/bump_version.py` script will be created to automate this:

```bash
# Bump patch version (0.1.0 → 0.1.1)
python scripts/bump_version.py patch

# Bump minor version (0.1.0 → 0.2.0)
python scripts/bump_version.py minor

# Bump major version (0.1.0 → 1.0.0)
python scripts/bump_version.py major
```

## Professional Workflow

### For Each Release:

1. **Make your changes** and commit them
2. **Update CHANGELOG.md** (if you have one) with what changed
3. **Bump the version** using the appropriate level
4. **Build the standalone app**:
   ```bash
   ./build/build_mac.sh
   ```
5. **Test the build** thoroughly
6. **Create a git tag**:
   ```bash
   git tag -a v0.1.1 -m "Release v0.1.1: Fixed propensity colors and error handling"
   ```
7. **Push to GitHub**:
   ```bash
   git push origin main
   git push origin v0.1.1
   ```
8. **Create a GitHub Release** (optional but recommended):
   - Go to GitHub → Releases → Create new release
   - Select your tag (v0.1.1)
   - Add release notes
   - Attach the built .app or .exe file

## Recommended Next Version

Based on the changes you've made:
- Fixed directory switching bug
- Fixed propensity colors
- Fixed deal size scaling
- Improved error handling
- Updated ring names

**Recommendation: Bump to 0.1.1** (patch release)

These are bug fixes and improvements, not new features, so a patch increment is appropriate.

## Future: Automated Versioning

For larger projects, consider:

1. **bump2version** - Python tool for version management
   ```bash
   pip install bump2version
   bump2version patch  # Automatically updates all files
   ```

2. **semantic-release** - Fully automated based on commit messages
   - Analyzes commit messages (fix:, feat:, BREAKING:)
   - Automatically determines version bump
   - Creates releases and changelogs

3. **GitHub Actions** - Automate releases on tag push
   - Automatically build and publish when you push a tag
   - See `.github/workflows/build-release.yml`

## Best Practices

1. **Update version in ONE place** - only `pyproject.toml`
2. **Tag every release** in git
3. **Write meaningful commit messages** for the version bump
4. **Test before releasing** - build and test the standalone app
5. **Keep a CHANGELOG.md** to track what changed in each version
6. **Use pre-release versions** for testing (e.g., 0.2.0-beta.1)
7. **Move to 1.0.0** when you're confident it's production-ready

## Example Changelog Entry

```markdown
## [0.1.1] - 2026-03-18

### Fixed
- Fixed propensity to win colors not displaying correctly in standalone builds
- Fixed deal size scaling not working properly
- Fixed directory switching keeping old projects loaded
- Improved error messages with user-friendly explanations

### Changed
- Updated ring names from quarterly (Q1-Q4) to half-yearly (Current HY, Next HY, Year +1, Year +2)
- Bundled config.yml now automatically used in standalone builds

### Added
- Server shutdown endpoint for proper directory switching
- Better validation error messages with actionable guidance
```

## Quick Reference

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Bug fix | PATCH | 0.1.0 → 0.1.1 |
| New feature | MINOR | 0.1.0 → 0.2.0 |
| Breaking change | MAJOR | 0.1.0 → 1.0.0 |
| Pre-release | Add suffix | 0.2.0-beta.1 |
| Production ready | Move to 1.x | 0.9.0 → 1.0.0 |