# WORKLOG — Taxo

**Оновлено:** 30.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.8-r3** / `v10.8-r3`  
**Latest integrated code checkpoint:** **10.8-r3** — `main` `50db4b0de4d37260c2031aa96317fef61d93ea90`  
**Issued fast-test:** **10.8-r6** — `v10.8-r6`, exact source `aeebe978e64b20a3e306ce1b6a45aa81600d5e89`; PR #109 лишається draft/unmerged  
**Active code revision:** **10.8-r7** — architecture for expansion / ordered feature-layer registry  
**Active branch:** `work/v10.8-r7-feature-layer-registry`  
**Active PR:** #110 — draft/open, base `work/v10.8-r6-main-modularization`  
**Live ledger:** Issue #61

## COMPLETED CHECKPOINT — 10.8-r6

- immutable tag/release `v10.8-r6`;
- exact source `aeebe978e64b20a3e306ce1b6a45aa81600d5e89`;
- publisher `36772171355` — success;
- exact-source regression **701/701 OK**;
- START `Taxo_v10_8_candidate_r6_START.zip`;
- START SHA-256 `bdc0e9f0fbc97c229d6b885756073e3def21ed23ac9004e085a915cb7898c0ef`;
- Windows gate `36772177378` — success;
- macOS arm64 + x86_64 gate `36772177353` — success;
- first `main.py` split: neutral file-output infrastructure moved to `output_files.py`;
- PR #109 not merged without owner command.

## ACTIVE — 10.8-r7

Тема: **закласти контрольовану архітектуру розширення, щоб нові модулі не роздували entry point і великий `main.py`.**

### Base / pre-flight

- r7 starts only from immutable r6 source `aeebe978e64b20a3e306ce1b6a45aa81600d5e89`;
- branch `work/v10.8-r7-feature-layer-registry`;
- draft PR #110 targets the r6 branch, so the PR diff contains only the new r7 slice;
- `main.APP_VERSION` and `VERSION.txt` are synchronized to `10.8-r7` by an exact one-shot guarded change;
- business DB/schema and user data are not changed.

### Implemented

- new `feature_layers.py` centralizes the ordered runtime extension chain;
- every runtime layer has a stable `feature_id`, installer, bootstrap flag and domain metadata;
- registry validates unique IDs, exactly one first bootstrap layer and callable installers;
- historical install order is preserved;
- `taxo_app.py` no longer contains the long nested revision-install expression and now builds the current `App` through `install_feature_layers(core)`;
- `START.bat` explicitly requires `feature_layers.py`;
- source package verification includes `feature_layers.py`;
- `tests/test_v10_8_r7.py` guards registry semantics, ordering and simplified entry point;
- r6 identity regression converted to a historical anchor so later revisions do not rewrite the r6 checkpoint;
- `docs/maintenance/AUDIT_EXTENSION_ARCHITECTURE_v10.8-r7.md` records the forward architecture: modular desktop monolith, domain/service/repository/UI boundaries and gradual reduction of new dependencies on global `main`;
- `docs/releases/RELEASE_NOTES_v10.8-r7.md` prepared.

### Architecture rule recorded

`feature_layers.py` is composition/compatibility infrastructure only. New large functions should become domain modules with narrow installers, not another indefinite chain of `vXXXX_features.py` wrappers. Cross-domain work should move toward explicit service/repository interfaces and read models while preserving existing plan/fact, history and data compatibility.

## DOING

1. Run exact-head source regression / START package and PR Windows + macOS gates for #110.
2. Fix any regression without broadening the r7 scope.
3. Publish immutable `v10.8-r7` START fast-test only after all mandatory gates are green.

## NEXT

After r7 is issued/frozen, continue only as **10.8-r8**. Preferred next architecture slice: small application/service context for shared infrastructure (workspace, DB connection factory, output services), then backup/migration extraction. Do not move business rules into the context and do not merge r7 into `main` without an explicit owner command.
