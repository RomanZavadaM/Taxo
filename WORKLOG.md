# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.5-r8** / `v10.5-r8`  
**Issued source:** `846e5c5111b14a4a1f2e49203803e86c495b458f`  
**Main merge:** PR #76 → `eb9cb039d35419fb579ff0f5e1b9c633c95ccd86`  
**Release workflow:** `36406419955` — success  
**Regression:** `483/483 OK`  
**Release:** https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8  
**Next code revision:** **10.5-r9** — not started  
**Live ledger:** Issue #61

## DONE — 10.5-r8

- [x] Windows 7 / Python 3.8 compatibility fix for the short openpyxl `tabId` TypeError signature.
- [x] Source XLSX remains unchanged; compatibility repair is in-memory only.
- [x] Unrelated `TypeError` cases are not swallowed.
- [x] Full source regression: **483/483 OK**.
- [x] PR checks: modern Windows + macOS ARM64 + macOS Intel — success.
- [x] Full candidate package set published:
  - START;
  - Windows x64 Setup/Portable;
  - Windows 7 SP1 x64 Setup/Portable;
  - macOS ARM64 Portable;
  - macOS Intel x86_64 Portable;
  - SHA-256 manifests.
- [x] tag/release `v10.5-r8` published against exact source `846e5c5111b14a4a1f2e49203803e86c495b458f`.
- [x] PR #76 merged into `main`.
- [x] checkpoint documentation synchronized.

## PRESERVED FROM 10.5-r7

- Diia-first personnel military-accounting reconciliation workflow;
- local preparation is explicitly separate from the official external Diia fixation fact;
- editable working registry values are separate from immutable government snapshots;
- employee documents register;
- vehicle / «Шлях» reconciliation and working data;
- enterprise military-transport statement;
- vehicle-document control, DЦВ, manual archive behaviour;
- plan/fact, waybill, attestation and schedule rules.

## NEXT

Start **10.5-r9** only after rereading `START_HERE.md`, `PROJECT_RULES.md`, `PROJECT_STATE.md`, this file and the latest Issue #61 entries. Use a new work branch; do not change or reissue r8.

## BLOCKED

Немає.
