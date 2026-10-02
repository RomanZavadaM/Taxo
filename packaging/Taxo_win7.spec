# -*- mode: python ; coding: utf-8 -*-

# Taxo Windows 7 SP1 x64 compatibility build.
# Kept separate from the modern Taxo.spec because PyInstaller 5.13.2
# does not support the newer Analysis() optimization argument.
from pathlib import Path
import sys
ROOT = Path.cwd()
SRC = ROOT / "src" / "taxo"
sys.path.insert(0, str(SRC))
from branding import generate_build_icons

BRAND_ICONS = generate_build_icons()

a = Analysis(
    [str(ROOT / 'taxo_app.py')],
    pathex=[str(ROOT), str(SRC)],
    binaries=[],
    datas=[
        (str(ROOT / 'assets' / 'Бланк підтвердження.docx'), 'assets'),
        (str(ROOT / 'assets' / 'attestation_visual_template.pdf'), 'assets'),
        (str(ROOT / 'LICENSE.md'), '.'),
        (str(ROOT / 'COPYRIGHT.md'), '.'),
        (str(ROOT / 'THIRD_PARTY_NOTICES.md'), '.'),
    ],
    hiddenimports=[
        'main', 'work_analysis_ext', 'activity_register_60', 'v9_release',
        'hotfix_901', 'v91_features', 'personnel_v91', 'work_regime',
        'workspace', 'tachograph', 'attestation_render', 'waybill',
        'branding', 'branding_asset', 'document_viewer', 'vehicle_documents',
        'fitz', 'pymupdf', 'win32print', 'win32ui', 'win32con', 'PIL.ImageWin',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
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
    icon=str(BRAND_ICONS['ico']),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='Taxo',
)
