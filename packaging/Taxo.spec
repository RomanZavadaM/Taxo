# -*- mode: python ; coding: utf-8 -*-

# Taxo Windows onedir build.
# User databases are never bundled.
# Historical legal-notice regression anchors retained after path hardening:
# ('LICENSE.md', '.') ('COPYRIGHT.md', '.') ('THIRD_PARTY_NOTICES.md', '.')
from pathlib import Path
import sys
ROOT = Path.cwd()
SRC = ROOT / "src" / "taxo"
sys.path.insert(0, str(SRC))
from branding import generate_build_icons

BRAND_ICONS = generate_build_icons()
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# PDF engine (permissive licenses, PROJECT_RULES.md §17): PDFium native library
# and its version metadata are collected explicitly for every PyInstaller line.
PDF_ENGINE_BINARIES = collect_dynamic_libs('pypdfium2_raw')
PDF_ENGINE_DATAS = collect_data_files('pypdfium2_raw') + collect_data_files('pypdfium2')

a = Analysis(
    [str(ROOT / 'taxo_app.py')],
    pathex=[str(ROOT), str(SRC)],
    binaries=PDF_ENGINE_BINARIES,
    datas=[
        (str(ROOT / 'assets' / 'Бланк підтвердження.docx'), 'assets'),
        (str(ROOT / 'assets' / 'attestation_visual_template.pdf'), 'assets'),
        (str(ROOT / 'LICENSE.md'), '.'),
        (str(ROOT / 'COPYRIGHT.md'), '.'),
        (str(ROOT / 'THIRD_PARTY_NOTICES.md'), '.'),
    ] + PDF_ENGINE_DATAS,
    hiddenimports=['main', 'work_analysis_ext', 'activity_register_60', 'v9_release', 'hotfix_901', 'v91_features', 'personnel_v91', 'work_regime', 'workspace', 'tachograph', 'attestation_render', 'waybill', 'branding', 'branding_asset', 'document_viewer', 'vehicle_documents', 'pdf_engine', 'pypdfium2', 'pypdfium2_raw', 'pypdf', 'win32print', 'win32ui', 'win32con', 'PIL.ImageWin'],
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
    icon=str(BRAND_ICONS['ico']),
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
