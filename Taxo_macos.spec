# -*- mode: python ; coding: utf-8 -*-

# Taxo 9.0 — native macOS application bundle.
# Build separately on Apple Silicon and Intel; user databases are forbidden.

a = Analysis(
    ['taxo_app.py'],
    pathex=[],
    binaries=[],
    datas=[('Бланк підтвердження.docx', '.'), ('attestation_visual_template.pdf', '.')],
    hiddenimports=['main', 'work_analysis_ext', 'activity_register_60', 'v9_release', 'workspace', 'tachograph', 'attestation_render', 'waybill', 'fitz', 'pymupdf'],
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
    upx=False,
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
    upx=False,
    name='Taxo',
)

app = BUNDLE(
    coll,
    name='Taxo.app',
    icon=None,
    bundle_identifier='com.romanzavadam.taxo',
    version='9.0',
    info_plist={
        'CFBundleDisplayName': 'Taxo',
        'CFBundleName': 'Taxo',
        'CFBundleShortVersionString': '9.0',
        'CFBundleVersion': '9.0',
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': True,
    },
)
