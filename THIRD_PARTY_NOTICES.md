# Third-party notices — Taxo 10.2-r9

Taxo is proprietary software. The components below retain their own licenses.
This file is a compliance index; exact upstream license/NOTICE files must be
collected for executable distributions.

## Runtime dependencies

| Component | Version | License / status | Purpose |
| --- | --- | --- | --- |
| python-docx | 1.2.0 | MIT | DOCX generation and reading |
| openpyxl | 3.1.5 | MIT | XLSX generation |
| ReportLab | 4.4.9 | BSD-family | PDF generation |
| Pillow | 11.3.0 | MIT-CMU | Image processing |
| pypdf | 6.19.0 | BSD-3-Clause | PDF template overlay / merge |
| pypdfium2 | 5.13.0 | Apache-2.0 / BSD-3-Clause; PDFium BSD-style | PDF-to-JPG rasterization |
| opencv-python-headless | 4.13.0.92 | wrapper MIT; OpenCV Apache-2.0; bundled notices also apply | Tachograph image processing |
| pywin32 | 311, Windows only | upstream project and bundled component licenses | Windows printing / integration |

## Runtime and build environment

- CPython is governed by the Python Software Foundation license and related
  historical notices when the runtime is bundled.
- PyInstaller is a build tool; its bootloader exception permits proprietary
  executable distribution subject to its license terms.
- Inno Setup is a Windows installer build tool and is not relicensed as Taxo.

## PDF stack decision in 10.2-r9

PyMuPDF / fitz is intentionally not a Taxo dependency from 10.2-r9 onward.
PDF viewing is delegated to the operating system or browser. PDF form stamping
uses ReportLab + pypdf. PDF-to-JPG conversion uses pypdfium2/PDFium.

pypdfium2/PDFium binary redistributions require the applicable PDFium and
bundled dependency license notices to accompany the binary. Taxo therefore
collects upstream license/NOTICE files before executable packaging.

## Distribution rule

Before a stable binary release:
1. collect exact license/NOTICE files from installed runtime distributions;
2. include them with the executable package;
3. regenerate/check the SBOM against the dependency set used for the build.
