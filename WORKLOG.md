# WORKLOG — Taxo

**Оновлено:** 25.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint:** `v10.4-r1` → `4970ee3497c9340c1c5f414d7a193071092ce70c`  
**Main:** `41e9652142518884108e6c6112618cb7b1dbe42b` before this docs-only audit  
**Windows 7 compatibility:** accepted and included in 10.4-r1  
**UI audit:** `docs/maintenance/AUDIT_UI_10_4_R1.md`  
**Live ledger:** Issue #61.

## DONE — UI AUDIT 10.4-r1

- [x] Reviewed main shell, header/sidebar, personnel workspace, employee timesheet, route editor, document viewer, vehicle documents, tachograph and cross-platform layout helpers.
- [x] Confirmed a real route-stop layout collision: «Зберегти» uses the same grid row as a form field.
- [x] Identified non-adaptive fixed-size document windows.
- [x] Identified missing horizontal scrollbars in multiple wide tables.
- [x] Identified personnel/report/timesheet horizontal and vertical overflow risks.
- [x] Identified navigation naming inconsistency «Працівники / Персонал / Водії».
- [x] Identified Win7 glyph, contrast, fixed-height and Linux-wheel polish issues.
- [x] Recorded prioritized remediation order in the audit document.

## NEXT

If UI remediation is started, the next code revision is **`10.4-r2`**. Start with P0/P1 from `AUDIT_UI_10_4_R1.md`; do not mix business-logic changes into this UI slice.

## BLOCKED

Немає.
