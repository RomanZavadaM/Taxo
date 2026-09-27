# WORKLOG — Taxo

**Оновлено:** 27.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest published full checkpoint:** `v10.4-r2` → `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Latest issued fast-test revision:** Taxo `10.4-r6`  
**Issued r6 head:** `d25cac1427911e2640db0be126c5f63410cb4e56`  
**r6 START:** run `36342480624`, artifact `10939860812`, regression `323/323 OK`  
**Active revision:** Taxo `10.4-r7`  
**Active branch:** `work/v10.4-r7-document-control-registry-separation`  
**Code head before final r7 gate:** `d7d5b230480ec5e0229a424c366ece84b413e539`  
**Stable `main`:** remains on integrated 10.4-r2 line; r3–r7 are fast-test development revisions unless separately merged/released  
**Live ledger:** Issue #61

## IMMUTABLE HISTORY — r3..r6

- `10.4-r3`: «Без тахо — 8 год» no longer destroys planned segments/routes; EDRPOU moved to common company requisites; runtime `9.0.1` title residue removed.
- `10.4-r4`: schedule audit made explicit; detects route-time vs route-point boundary mismatch; waybill time is not silently rewritten.
- `10.4-r5`: personnel registry XLSX parser, personnel/military profile basis, import history/snapshots, employee document register.
- `10.4-r6`: Regulation №340 plan/fact separation; exact split/cross-midnight work intervals; valid `3+9` daily rest no longer generates legacy false positives; issued and immutable.

## DOING — Taxo 10.4-r7

### 1. Restore existing local vehicle-document control

Owner clarification: current vehicle-document control was correct and must remain a separate operational subsystem.

Implemented:

- [x] fixed crash `cannot use geometry manager grid ... which already has slaves managed by pack` in `open_vehicle_document_control`;
- [x] `Treeview` and scrollbars now live inside one dedicated `table` frame managed with `grid`, while the frame itself is managed with `pack`;
- [x] business rules of `vehicle_document_summary`, `control_rows`, expiry checks and waybill document warnings are not replaced by registry data;
- [x] local vehicle documents remain: insurance, optional additional liability insurance, diagnostics/technical inspection, registration certificate, temporary registration when required, tachograph inspection protocol, copies/history and expiry control.

### 2. Hard boundary: local documents != state registries

Permanent rule recorded in `PROJECT_RULES.md` and `docs/architecture/REGISTRY_AND_LOCAL_DOCUMENTS_BOUNDARY.md`.

- [x] current local vehicle-document control uses only Taxo `vehicle_documents`;
- [x] state registry data must not feed `vehicle_document_summary`, `control_rows` or waybill document warnings;
- [x] personnel state extracts are for personal/military-accounting data;
- [x] `Шлях` is for vehicle/licensing-file data known to the state;
- [x] absence/presence in a state registry is not equivalent to absence/presence of an enterprise document.

### 3. Registry reconciliation semantics

Owner decision implemented for personnel registry import and fixed as the generic model for future `Шлях` import.

Three explicit modes:

1. **Лише звірити** — compare and record the reconciliation snapshot; no working Taxo fields are changed.
2. **Доповнити** — fill only empty local fields / add new registry information.
3. **Оновити з реєстру + доповнити** — replace only fields that are actually present and non-empty in the fresh registry extract, and add new information.

Invariant for every mode:

- [x] an empty registry field never clears a Taxo field;
- [x] a Taxo record/field absent from the extract is never deleted, archived or zeroed automatically;
- [x] local employees absent from the current extract are shown as **«Є у Taxo, але відсутній у цьому витягу»** for analysis;
- [x] ambiguous/conflicting matches are not overwritten automatically;
- [x] compare-only does not mutate the local employee document register;
- [x] source filename, SHA-256, snapshot/history and mode are retained for audit.

### 4. Quarterly freshness

- [x] base cadence = **once per calendar quarter**, not rolling 90 days;
- [x] Q1 Jan–Mar, Q2 Apr–Jun, Q3 Jul–Sep, Q4 Oct–Dec;
- [x] if a successful reconciliation exists in the current quarter → `Актуально`;
- [x] first day of the next quarter → `Потрібне звіряння`;
- [x] manual fresh import/reconciliation is allowed at any time;
- [x] personnel page button displays current-quarter status and refreshes after import.

## REGISTRY ROADMAP

### Personnel / military accounting

- continue aligning structured military accounting with the current 2026 legal model;
- maintain state extracts as recurring reconciliation snapshots, not one-time imports;
- add full field-level colour reconciliation: green=match, blue=can enrich, yellow=difference, red=critical identity/status conflict, grey=not checked/not applicable;
- preserve the action model: accept registry / keep Taxo / needs correction in registry / defer;
- build required military-accounting reports from structured local data, with registry extracts used as verification/enrichment sources.

### Vehicles / `Шлях`

Real XLSX format has been received and mapped without publishing real VIN/plates.

Next implementation:

- parser + upload form for `Шлях` XLSX/CSV;
- VIN as primary reconciliation key, plate as secondary control key;
- compare kind, plate, carrier, registry status, VIN, make, model, gross mass, EURO and ECMT fields;
- same three modes: compare / fill empty / update non-empty registry fields + fill;
- never delete or clear Taxo vehicle data because it is absent from the extract;
- `Знятий з обліку` is a state-registry/licensing status and never automatically deletes a Taxo vehicle;
- show Taxo-only vehicles separately to understand what the current state extract does not confirm;
- quarterly reminder and snapshot history exactly like personnel reconciliation.

### Military-transport accounting

Later separate module: vehicle military-accounting data and current reporting under the applicable 2026 rules, based on structured local vehicle/personnel data. State-registry extracts remain verification/enrichment inputs, not replacements for enterprise records.

## NEXT

1. Run final r7 regression on the clean branch head.
2. Build/verify a new `Taxo_v10_4_candidate_r7_START` artifact.
3. Record exact test count, run/artifact/SHA in Issue #61 and here.
4. After r7 is issued, do not reuse r7; next code revision = `10.4-r8`.
5. r8 priority: real `Шлях` parser/upload + vehicle reconciliation panel unless owner reprioritizes.

## BLOCKED

None. Real personnel registry XLSX layouts and real `Шлях` XLSX structure are available; personal/registry data must never be published to the repository or test package.
