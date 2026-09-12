# -*- mode: python ; coding: utf-8 -*-

# Taxo v8.65 candidate r3 — Windows onedir build.
# User databases are NOT bundled; Taxo stores them under
# %USERPROFILE%\Documents\DriverWorktime\.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('Бланк підтвердження.docx', '.'), ('attestation_visual_template.pdf', '.')],
    hiddenimports=['tachograph', 'attestation_render', 'fitz', 'pymupdf'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Taxo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Taxo',
)
