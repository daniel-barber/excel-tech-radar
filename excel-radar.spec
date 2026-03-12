# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Excel Tech Radar
Builds standalone executables for Mac and Windows
"""

import sys
from pathlib import Path

block_cipher = None

# Determine platform-specific settings
is_mac = sys.platform == 'darwin'
is_windows = sys.platform == 'win32'

# Application metadata
app_name = 'Radar Studio'
bundle_identifier = 'com.radarstudio.app'

# Data files to include
datas = [
    ('web', 'web'),                          # Web UI files
    ('templates', 'templates'),              # Excel templates
    ('config.yml', '.'),                     # Configuration
    ('README.md', '.'),                      # Documentation
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'openpyxl',
    'openpyxl.cell',
    'openpyxl.styles',
    'openpyxl.utils',
    'pandas',
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    'yaml',
    'bleach',
    'flask',
    'flask_cors',
    'werkzeug',
    'jinja2',
    'click',
    'typer',
    'rich',
    'tkinter',
]

# Analysis: Find all Python files and dependencies
a = Analysis(
    ['src/excel_radar/launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.testing',
        'pytest',
        'setuptools',
        'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ: Create Python archive
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# Platform-specific executable configuration
if is_mac:
    # macOS: Create .app bundle
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='excel-radar-launcher',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,  # No console window on Mac
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='excel-radar-launcher',
    )
    
    app = BUNDLE(
        coll,
        name='Radar Studio.app',
        icon='build/icons/icon.icns',
        bundle_identifier=bundle_identifier,
        info_plist={
            'CFBundleName': 'Radar Studio',
            'CFBundleDisplayName': 'Radar Studio',
            'CFBundleVersion': '0.1.0',
            'CFBundleShortVersionString': '0.1.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13.0',
        },
    )

elif is_windows:
    # Windows: Create .exe
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='RadarStudio',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # No console window on Windows
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='build/icons/icon.ico',
    )

else:
    # Linux or other: Create standard executable
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='excel-radar-launcher',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='excel-radar-launcher',
    )