# Taxo — rights and distribution model

Status fixed on 21.09.2026.

## Rights holder

- Rights holder: **Роман Завада (Roman Zavada), natural person**.
- Taxo is his **personal proprietary software product**.
- Ownership of an enterprise operated by the same person does not by itself
  transfer intellectual-property rights in Taxo to that enterprise.

## Repository model

The GitHub repository remains **public** for the current development model.
Public source visibility is not an open-source grant. Taxo uses its own
proprietary LICENSE and all rights not expressly granted remain reserved.

Because source code has already been published, Taxo does not rely on source
code secrecy as its principal legal protection.

## Commercial distribution

Customers should receive an executable package and a separate written right to
use Taxo. Ownership of the software is not transferred merely because a copy is
installed or paid for.

Customer operational data remains separate from software ownership.

## AI-assisted development

AI tools are used as development assistance. OpenAI is not named as Taxo's
copyright holder or publisher. Third-party code and libraries remain governed
by their own licenses.

## PDF policy from 10.2-r9

- no PyMuPDF / fitz dependency;
- PDF files are opened through the OS/browser for viewing;
- ReportLab + pypdf are used to create/stamp PDFs;
- pypdfium2/PDFium is used only where rasterization is required for JPG output.

## Release compliance gate

Every stable executable release should include:
1. Taxo LICENSE and COPYRIGHT;
2. THIRD_PARTY_NOTICES.md;
3. an SBOM for the release dependency set;
4. collected upstream license/NOTICE files required for binary redistribution.
