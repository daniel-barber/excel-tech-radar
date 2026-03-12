# Packaging Guide for Excel Tech Radar

This document describes how to create standalone executables for Excel Tech Radar on macOS and Windows.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Local Building](#local-building)
- [Automated Builds (CI/CD)](#automated-builds-cicd)
- [Testing Builds](#testing-builds)
- [Distribution](#distribution)
- [Troubleshooting](#troubleshooting)
- [Code Signing](#code-signing)

## Overview

Excel Tech Radar uses PyInstaller to create standalone executables that bundle:
- Python interpreter
- All Python dependencies
- Web UI assets (HTML, CSS, JS)
- Excel templates
- Configuration files

Users can run the application without installing Python or any dependencies.

### Build Outputs

| Platform | Output | Size | Format |
|----------|--------|------|--------|
| macOS | Excel Tech Radar.app | ~80 MB | .app bundle + optional .dmg |
| Windows | ExcelTechRadar.exe | ~60 MB | .exe + optional .zip |

## Prerequisites

### macOS

```bash
# Python 3.11 or higher
python3 --version

# Xcode Command Line Tools (for DMG creation)
xcode-select --install

# PyInstaller (installed automatically by build script)
pip install pyinstaller>=6.0.0
```

### Windows

```cmd
REM Python 3.11 or higher
python --version

REM PyInstaller (installed automatically by build script)
pip install pyinstaller>=6.0.0

REM Optional: 7-Zip for ZIP creation
REM Download from: https://www.7-zip.org/
```

## Local Building

### Quick Start

**macOS:**
```bash
./build/build_mac.sh
```

**Windows:**
```cmd
build\build_windows.bat
```

### Manual Build Process

If you need more control over the build process:

#### 1. Install Build Dependencies

```bash
pip install -e ".[build]"
```

#### 2. Run PyInstaller

```bash
pyinstaller excel-radar.spec --clean --noconfirm
```

#### 3. Test the Build

**macOS:**
```bash
open "dist/Excel Tech Radar.app"
```

**Windows:**
```cmd
dist\ExcelTechRadar.exe
```

### Build Configuration

The build is configured in `excel-radar.spec`:

```python
# Key configuration options:

# Data files to include
datas = [
    ('web', 'web'),              # Web UI
    ('templates', 'templates'),  # Excel templates
    ('config.yml', '.'),         # Configuration
]

# Hidden imports (dependencies PyInstaller might miss)
hiddenimports = [
    'openpyxl',
    'pandas',
    'pydantic',
    # ... more
]

# Exclude unnecessary packages
excludes = [
    'matplotlib',
    'numpy.testing',
    'pytest',
]
```

### Customizing the Build

#### Change App Name

Edit `excel-radar.spec`:
```python
app_name = 'Your Custom Name'
```

#### Add Icon

1. Create icon files:
   - macOS: `icon.icns` (512x512 PNG converted to ICNS)
   - Windows: `icon.ico` (256x256 PNG converted to ICO)

2. Update spec file:
```python
# macOS
app = BUNDLE(
    ...
    icon='icon.icns',
)

# Windows
exe = EXE(
    ...
    icon='icon.ico',
)
```

#### Reduce Size

1. Enable UPX compression (already enabled):
```python
upx=True,
```

2. Exclude more packages:
```python
excludes=[
    'matplotlib',
    'scipy',
    'PIL',
]
```

3. Use one-file mode (slower startup):
```python
exe = EXE(
    ...
    a.binaries,
    a.zipfiles,
    a.datas,
    ...
)
```

## Automated Builds (CI/CD)

### GitHub Actions Workflow

Builds are automatically triggered by:

1. **Version Tags**: Push a tag like `v0.1.0`
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. **Manual Trigger**: Use GitHub Actions UI
   - Go to Actions tab
   - Select "Build and Release"
   - Click "Run workflow"
   - Enter version number

### Workflow Steps

The `.github/workflows/build-release.yml` workflow:

1. **Build macOS**
   - Runs on `macos-latest`
   - Creates `.app` bundle
   - Generates `.dmg` installer
   - Uploads artifacts

2. **Build Windows**
   - Runs on `windows-latest`
   - Creates `.exe` executable
   - Generates `.zip` archive
   - Uploads artifacts

3. **Create Release**
   - Creates GitHub release
   - Attaches build artifacts
   - Generates release notes

### Monitoring Builds

View build status:
- GitHub Actions tab
- Commit status checks
- Email notifications (if configured)

## Testing Builds

### Pre-Release Testing

Before distributing, test on clean systems:

#### macOS Testing

1. **Test on clean Mac** (no Python installed)
   ```bash
   # Copy .app to test machine
   open "Excel Tech Radar.app"
   ```

2. **Test Gatekeeper**
   - Right-click app
   - Select "Open"
   - Confirm security warning

3. **Test functionality**
   - Launch app
   - Select data directory
   - Start server
   - Open browser
   - Load Excel file
   - Verify visualization

#### Windows Testing

1. **Test on clean Windows** (no Python installed)
   ```cmd
   REM Extract ZIP
   REM Run executable
   ExcelTechRadar.exe
   ```

2. **Test Windows Defender**
   - May show SmartScreen warning
   - Click "More info"
   - Click "Run anyway"

3. **Test functionality**
   - Same as macOS testing

### Automated Testing

The `.github/workflows/test.yml` workflow runs:

- Unit tests on all platforms
- Build verification
- Code quality checks

## Distribution

### GitHub Releases

1. **Create Release**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. **Download from Releases**
   - Users visit: `https://github.com/yourusername/excel-tech-radar/releases`
   - Download platform-specific file
   - Follow installation instructions

### Direct Distribution

For internal distribution:

1. **macOS**: Share `.dmg` file
   - Users drag to Applications
   - First launch: right-click > Open

2. **Windows**: Share `.zip` file
   - Users extract to folder
   - Run `.exe` file
   - May need to approve in Windows Defender

### Installation Instructions

Include in release notes:

**macOS:**
```markdown
1. Download ExcelTechRadar-{version}-macOS.dmg
2. Open the DMG file
3. Drag "Excel Tech Radar" to Applications folder
4. Right-click the app and select "Open" (first time only)
5. Click "Open" in the security dialog
```

**Windows:**
```markdown
1. Download ExcelTechRadar-{version}-Windows.zip
2. Extract the ZIP file to a folder
3. Run ExcelTechRadar.exe
4. If Windows Defender shows a warning:
   - Click "More info"
   - Click "Run anyway"
```

## Troubleshooting

### Build Issues

#### "Module not found" Error

**Problem**: PyInstaller can't find a module

**Solution**: Add to `hiddenimports` in `excel-radar.spec`:
```python
hiddenimports = [
    'missing_module',
]
```

#### Build Succeeds but App Won't Launch

**Problem**: Missing data files

**Solution**: Add to `datas` in `excel-radar.spec`:
```python
datas = [
    ('path/to/file', 'destination'),
]
```

#### App Too Large

**Problem**: Executable is too big

**Solutions**:
1. Enable UPX compression
2. Exclude unnecessary packages
3. Use one-file mode
4. Remove unused dependencies

### Runtime Issues

#### macOS: "App is damaged and can't be opened"

**Problem**: Gatekeeper blocking unsigned app

**Solution**:
```bash
# Remove quarantine attribute
xattr -cr "Excel Tech Radar.app"

# Or disable Gatekeeper temporarily
sudo spctl --master-disable
```

#### Windows: "Windows protected your PC"

**Problem**: SmartScreen blocking unsigned app

**Solution**:
1. Click "More info"
2. Click "Run anyway"

#### App Crashes on Startup

**Problem**: Missing dependencies or data files

**Solution**:
1. Check console output
2. Verify data files are bundled
3. Test with `--debug` flag

### Testing Issues

#### Can't Test on Clean System

**Problem**: Need Python-free environment

**Solutions**:
1. Use virtual machine
2. Use Docker container
3. Ask colleague to test
4. Use CI/CD for automated testing

## Code Signing

### macOS Code Signing

Required for distribution outside organization:

```bash
# 1. Get Developer ID certificate from Apple
# 2. Sign the app
codesign --deep --force --verify --verbose \
    --sign "Developer ID Application: Your Name (TEAM_ID)" \
    --options runtime \
    "dist/Excel Tech Radar.app"

# 3. Create signed DMG
hdiutil create -volname "Excel Tech Radar" \
    -srcfolder "dist/Excel Tech Radar.app" \
    -ov -format UDZO \
    "dist/ExcelTechRadar-signed.dmg"

# 4. Notarize with Apple
xcrun notarytool submit "dist/ExcelTechRadar-signed.dmg" \
    --apple-id "your@email.com" \
    --password "app-specific-password" \
    --team-id "TEAM_ID" \
    --wait

# 5. Staple notarization ticket
xcrun stapler staple "dist/ExcelTechRadar-signed.dmg"
```

### Windows Code Signing

Required for avoiding SmartScreen warnings:

```cmd
REM 1. Get code signing certificate
REM 2. Sign the executable
signtool sign /f certificate.pfx /p password ^
    /t http://timestamp.digicert.com ^
    /fd SHA256 ^
    dist\ExcelTechRadar.exe

REM 3. Verify signature
signtool verify /pa dist\ExcelTechRadar.exe
```

### Certificate Providers

- **macOS**: Apple Developer Program ($99/year)
- **Windows**: 
  - DigiCert (~$400/year)
  - Sectigo (~$200/year)
  - GlobalSign (~$250/year)

## Release Checklist

Before releasing a new version:

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run tests locally: `pytest`
- [ ] Build locally and test
- [ ] Update documentation
- [ ] Create git tag: `git tag v0.1.0`
- [ ] Push tag: `git push origin v0.1.0`
- [ ] Monitor GitHub Actions build
- [ ] Test downloaded artifacts
- [ ] Update release notes
- [ ] Announce release

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Apple Code Signing Guide](https://developer.apple.com/support/code-signing/)
- [Windows Code Signing Guide](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)

## Support

For packaging issues:
- Check [build/README.md](build/README.md)
- Review GitHub Actions logs
- Open an issue on GitHub