# WORKLOG — Taxo

**Оновлено:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.8-r3** / `v10.8-r3`  
**Latest integrated code checkpoint:** **10.8-r3** — `main` `50db4b0de4d37260c2031aa96317fef61d93ea90`  
**Latest issued fast-test:** **10.8-r9** — `v10.8-r9`, exact source `d8d29c79b82b53a0ad07df18dbbe19cf5f5d00c1`; PR #112 draft/unmerged  
**Issued r9 START:** `Taxo_v10_8_candidate_r9_START.zip` · SHA-256 `f1d37e4111ff780f46dc3736bdec093ee31e95ba896437d9902b87967113b0ac`  
**Active code revision:** **10.8-r10**  
**Active branch:** `work/v10.8-r10-database-runtime-infrastructure`  
**Active PR:** #113 — draft, base exact r9 branch  
**Live ledger:** Issue #61

## COMPLETED CHECKPOINT — 10.8-r9

Тема: **backup / restore / legacy migration infrastructure boundary**.

- immutable tag/prerelease `v10.8-r9`;
- exact source `d8d29c79b82b53a0ad07df18dbbe19cf5f5d00c1`;
- publisher run `36823663607` — success;
- source package run `36823663413` — success;
- exact-source regression **719/719 OK**;
- Windows gate `36823668396` — success;
- macOS gate `36823668394` — success;
- START `Taxo_v10_8_candidate_r9_START.zip`;
- START SHA-256 `f1d37e4111ff780f46dc3736bdec093ee31e95ba896437d9902b87967113b0ac`;
- низькорівневі backup/restore/legacy migration mechanics винесені у `backup_migration.py`;
- `main.py` зберігає compatibility wrappers;
- PR #112 лишається draft/unmerged;
- r9 заморожений: будь-яка наступна кодова зміна — r10.

## ACTIVE — 10.8-r10

Тема: **винести SQLite connection policy з великого `main.py` у вузький `database_runtime.py` без зміни DB/workspace/domain/UI semantics.**

### Base / pre-flight

- r10 почато від exact issued r9 source `d8d29c79b82b53a0ad07df18dbbe19cf5f5d00c1`;
- branch `work/v10.8-r10-database-runtime-infrastructure`;
- draft PR #113, base `work/v10.8-r9-backup-migration-infrastructure`;
- `VERSION.txt` і `main.APP_VERSION` = `10.8-r10`;
- `main` не змінювався і лишається на integrated `10.8-r3`;
- stable `v10.3` не змінюється.

### Implemented

- додано `database_runtime.py`;
- `connect_database(path)` володіє тільки низькорівневою SQLite connection policy;
- збережено timeout 30 с, `sqlite3.Row`, `foreign_keys=ON`, `busy_timeout=30000`, `journal_mode=DELETE`, `synchronous=FULL`;
- `main.db()` лишився compatibility wrapper і передає актуальний `DB_PATH`, тому runtime workspace switching не кешує старий шлях;
- `sqlite3` import у `main.py` не видалявся, бо він ще потрібний іншим exception paths;
- `START.bat` вимагає `database_runtime.py`;
- додано `tests/test_v10_8_r10.py`;
- додано `docs/maintenance/AUDIT_DATABASE_RUNTIME_INFRASTRUCTURE_v10.8-r10.md`;
- додано `docs/releases/RELEASE_NOTES_v10.8-r10.md`;
- одноразовий workflow для безпечного точкового patch великого `main.py` виконався успішно і самовидалився;
- PR #113 створено draft/open; у `main` нічого не зливалося.

### Regression fixes before issuance

Перший r10 source gate коректно зловив дві не-бізнесові проблеми. Обидві виправлені в незамороженій r10 до issuance:

- історичний `tests/test_v10_8_r9.py` більше не вимагає, щоб поточна версія назавжди дорівнювала r9; r9 лишився historical anchor, як попередні slices;
- `START.bat` повернуто до Windows **CRLF** без втрати нового `database_runtime.py` package guard; це зберігає старий START hardening contract.

Після цих виправлень запускаються нові exact-head source/Windows/macOS gates; старі невдалі/проміжні runs не є issuance evidence.

## DOING

1. Дочекатися нових exact-head source/Windows/macOS PR gates для #113.
2. Виправити тільки фактичні regression/packaging проблеми, якщо gates їх покажуть.
3. Додати immutable r10 publisher і видати fast-test тільки після повного green exact-head verify.
4. Після issuance записати exact source, run IDs, START SHA та direct link у Issue #61 і PR #113.

## NEXT

Після issuance `10.8-r10` будь-яка кодова зміна — **10.9-r1**. Наступний architecture slice визначати окремо і не змішувати infrastructure extraction з domain/UI remodel. Не зливати #113, #112 чи попередні draft PR у `main` без прямої команди власника.
