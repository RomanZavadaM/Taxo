# -*- mode: python ; coding: utf-8 -*-

# Taxo 9.1 candidate r9.7 — Windows onedir build.
# User databases are never bundled.

a = Analysis(
    ['taxo_app.py'],
    pathex=[],
    binaries=[],
    datas=[('Бланк підтвердження.docx', '.'), ('attestation_visual_template.pdf', '.')],
    hiddenimports=['main', 'work_analysis_ext', 'activity_register_60', 'v9_release', 'hotfix_901', 'v91_features', 'personnel_v91', 'work_regime', 'workspace', 'tachograph', 'attestation_render', 'waybill', 'fitz', 'pymupdf'],
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
