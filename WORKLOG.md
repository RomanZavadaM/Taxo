# WORKLOG — Taxo

**Оновлено:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.8-r3** / `v10.8-r3`  
**Latest integrated code checkpoint:** **10.8-r3** — `main` `50db4b0de4d37260c2031aa96317fef61d93ea90`  
**Latest issued fast-test:** **10.8-r8** — `v10.8-r8`, exact source `60cfcc6784be151ee7141a81fea0a67ad74e75f6`; PR #111 draft/unmerged  
**Issued r8 START:** `Taxo_v10_8_candidate_r8_START.zip` · SHA-256 `f87527d4de273d92cf8e6434b54da3ade6faa65c7795a75ed41422a3ea2f473c`  
**Active code revision:** **10.8-r9**  
**Active branch:** `work/v10.8-r9-backup-migration-infrastructure`  
**Active PR:** ще не відкритий  
**Live ledger:** Issue #61

## COMPLETED CHECKPOINT — 10.8-r8

Тема: **explicit application-services boundary для подальшого масштабування Taxo**.

- immutable tag/prerelease `v10.8-r8`;
- exact source `60cfcc6784be151ee7141a81fea0a67ad74e75f6`;
- publisher run `36775504122` — success;
- exact-source regression **713/713 OK**;
- source/START package run `36775504209` — success;
- Windows gate `36775510309` — success;
- macOS gate `36775510038` — arm64 + x86_64 success;
- START `Taxo_v10_8_candidate_r8_START.zip`;
- START SHA-256 `f87527d4de273d92cf8e6434b54da3ade6faa65c7795a75ed41422a3ea2f473c`;
- `application_context.py` дає новим modules explicit infrastructure services;
- legacy installers збережені;
- PR #111 лишається draft/unmerged і не зливається без окремої команди власника.

## ACTIVE — 10.8-r9

Тема: **винести backup / restore / legacy migration mechanics з великого `main.py` у вузький infrastructure module без зміни user-data semantics.**

### Base / pre-flight

- r9 почато тільки від exact issued r8 source `60cfcc6784be151ee7141a81fea0a67ad74e75f6`;
- branch `work/v10.8-r9-backup-migration-infrastructure`;
- `VERSION.txt` і `main.APP_VERSION` = `10.8-r9`;
- `main` не змінювався і лишається на integrated `10.8-r3`;
- stable `v10.3` не змінюється.

### Implemented

- додано `backup_migration.py`;
- винесено пошук legacy БД і one-time migration;
- винесено SQLite backup і 24-hour auto-backup guard;
- винесено validation резервної Taxo БД;
- винесено atomic restore через temporary DB;
- збережено safety backup перед restore і best-effort rollback при помилці;
- `main.py` лишає compatibility wrappers зі старими public names;
- infrastructure module не імпортує Tkinter/UI і не містить domain rules;
- `START.bat` вимагає `backup_migration.py`;
- `tests/test_v10_8_r9.py` покриває identity, wrappers, backup consistency, restore safety, no-overwrite legacy migration і UI boundary;
- `docs/maintenance/AUDIT_BACKUP_MIGRATION_INFRASTRUCTURE_v10.8-r9.md` додано;
- `docs/releases/RELEASE_NOTES_v10.8-r9.md` додано.

### Verify already green

- source/START run `36776021724` на head `367c24ee87610ad44c97b9e42dd3eb47b1116a4d` — success;
- regression, START creation, clean-package verification — success;
- після docs commits потрібен новий exact-head verify/PR CI перед issuance.

## DOING

1. Відкрити draft PR r9 проти immutable r8 branch.
2. Додати immutable source publisher `v10.8-r9` з exact-head regression і START verification.
3. Дочекатися нового exact-head source, Windows та macOS gates.
4. Якщо gates green — видати immutable `v10.8-r9` START fast-test і записати SHA/source у Issue #61 та PR.

## NEXT

Після issuance r9 будь-яка кодова зміна — тільки **10.8-r10**. Наступний architecture slice визначити після r9 за принципом: infrastructure не змішувати з domain rules; нові великі можливості будувати як окремі domain/service/repository/UI modules із вузькою точкою підключення. Не зливати r9 чи попередні draft PR у `main` без прямої команди власника.
