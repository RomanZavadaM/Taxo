# Third-party notices — Taxo

Taxo is proprietary software, but it uses third-party components under their own licenses. This file records the direct runtime dependencies used by Taxo 10.2-r9. Distribution packages must preserve the applicable license/copyright notices shipped by these projects and by their transitive/bundled components.

| Component | Version | License family | Purpose |
|---|---:|---|---|
| python-docx | 1.2.0 | MIT | DOCX generation/reading |
| openpyxl | 3.1.5 | MIT | XLSX generation |
| ReportLab | 4.4.9 | BSD | PDF report generation |
| Pillow | 11.3.0 | MIT-CMU | image processing/rendering |
| opencv-python-headless | 4.13.0.92 | MIT wrapper / OpenCV Apache-2.0; wheel includes additional third-party notices | image/tachograph processing |
| pywin32 | 311 (Windows only) | project includes components under multiple permissive licenses/notices | Windows printing/integration |
| Python runtime | 3.13 in START workflow | PSF License | runtime |

## Removed in 10.2-r9

**PyMuPDF / fitz** was removed from Taxo because its AGPL/commercial dual licensing is not appropriate for the intended proprietary distribution model without a separate commercial license. PDF files are now opened by the operating system/default browser or PDF application.

## Packaging rule

Before a stable commercial binary release, the build process must collect the exact license files/notices bundled by installed direct and transitive dependencies. This summary is not a substitute for those original license texts.
