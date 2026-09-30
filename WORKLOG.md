# WORKLOG — Taxo

**Оновлено:** 30.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.8-r3** / `v10.8-r3`  
**Latest integrated code checkpoint:** **10.8-r3** — `main` `50db4b0de4d37260c2031aa96317fef61d93ea90`  
**Latest issued fast-test:** **10.8-r7** — `v10.8-r7`, exact source `2786860d6ca36147745ffeca4b17746642381c53`; PR #110 draft/unmerged  
**Active code revision:** **10.8-r8** — explicit application-services context for future expansion  
**Active branch:** `work/v10.8-r8-application-context`  
**Active PR:** to be opened against the r7 branch after the r8 slice is assembled  
**Live ledger:** Issue #61

## COMPLETED CHECKPOINT — 10.8-r7

- immutable tag/prerelease `v10.8-r7`;
- exact source `2786860d6ca36147745ffeca4b17746642381c53`;
- publisher `36774146660` — success;
- exact-source regression **707/707 OK**;
- source/START package `36774146335` — success;
- Windows exact-head gate `36774150994` — success;
- macOS exact-head gate `36774150873` — arm64 + x86_64 success;
- START `Taxo_v10_8_candidate_r7_START.zip`;
- START SHA-256 `cd54d2ff0ab663445778c1e12c00beebaf40acde1c1834fb6de03d2195156e70`;
- direct START: `https://github.com/RomanZavadaM/Taxo/releases/download/v10.8-r7/Taxo_v10_8_candidate_r7_START.zip`;
- runtime feature composition moved to ordered `feature_layers.py` registry;
- architecture direction fixed: new large capabilities should be domain/service/repository/UI modules with narrow installers;
- PR #110 remains draft and is not merged without owner command.

## ACTIVE — 10.8-r8

Тема: **дати новим модулям вузьку explicit infrastructure boundary, щоб ріст Taxo не створював нові залежності від глобального `main`.**

### Base / pre-flight

- r8 starts only from immutable r7 source `2786860d6ca36147745ffeca4b17746642381c53`;
- branch `work/v10.8-r8-application-context`;
- `VERSION.txt` and `main.APP_VERSION` synchronized to `10.8-r8`;
- DB schema, workspace format and user data are unchanged.

### Implemented

- new `application_context.py` with `WorkspaceServices`, `OutputServices`, `ApplicationServices`;
- workspace root/path lookup is dynamic, not cached, so a switched workspace cannot leave future modules pointed at the old DB;
- `WorkspaceServices.connect_main_db()` provides fresh connections to the current workspace DB;
- output infrastructure is exposed through a narrow contract instead of requiring new modules to import `main`;
- `FeatureLayer` gained opt-in `uses_services=True` metadata;
- legacy installers keep their historical signatures; future context-aware layers can receive `services` explicitly;
- composed `App` exposes the same context as `App.services` for new UI/domain adapters;
- `taxo_app.py` builds one `SERVICES` context and passes it into `install_feature_layers`;
- `START.bat` and source package verification require `application_context.py`;
- `tests/test_v10_8_r8.py` covers workspace switching, DB connection, legacy/context-aware installer compatibility, fail-fast behavior and runtime wiring;
- `docs/maintenance/AUDIT_APPLICATION_CONTEXT_v10.8-r8.md` records the infrastructure/business boundary;
- `docs/releases/RELEASE_NOTES_v10.8-r8.md` prepared.

### Architecture rule recorded

`ApplicationServices` is infrastructure only, **not** a service locator for business rules. Plan/fact, timesheet, Attestations, STOIR, personnel, military accounting and other domain logic must remain in explicit domain/service modules. New large features should consume shared infrastructure through the context and expose their own narrow domain APIs.

## DOING

1. Open draft r8 PR against immutable r7 branch.
2. Run exact-head source regression / START package and Windows + macOS gates.
3. Fix only r8 architecture regressions without broadening scope.
4. Publish immutable `v10.8-r8` START fast-test after all gates are green.

## NEXT

After r8 is issued/frozen, continue only as **10.8-r9**. Preferred next architecture slice: extract backup/migration orchestration from `main.py` onto the explicit workspace/application-services boundary without changing backup format, restore semantics or user data. Do not merge r8 into `main` without an explicit owner command.
