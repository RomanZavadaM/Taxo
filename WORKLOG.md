# WORKLOG — Taxo

**Оновлено:** 30.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.8-r3** / `v10.8-r3`  
**Latest integrated code checkpoint:** **10.8-r3** — `main` `50db4b0de4d37260c2031aa96317fef61d93ea90`  
**Issued fast-test:** **10.8-r5** — `v10.8-r5`, exact source `fc9be91a892ae8be14b04c27b386da120061ec38`; PR #108 лишається draft/unmerged  
**Active code revision:** **10.8-r6** — контрольована декомпозиція oversized `main.py`  
**Active branch:** `work/v10.8-r6-main-modularization`  
**Active PR:** #109 — draft/open, base `work/v10.8-r5-stoir-forecast-repair-requests`  
**Live ledger:** Issue #61

## COMPLETED CHECKPOINT — 10.8-r5

- immutable tag/release `v10.8-r5`;
- exact source `fc9be91a892ae8be14b04c27b386da120061ec38`;
- exact-source regression **695/695 OK**;
- START `Taxo_v10_8_candidate_r5_START.zip`;
- START SHA-256 `834a5a57d5f97e3afd7b84c0c96e361a8ef4f32c7a88110684a5cddda400576c`;
- Windows gate success;
- macOS arm64 + x86_64 gates success;
- виправлено `no such column: worklog_id` на історичних робочих БД;
- PR #108 не злитий у `main` без команди власника.

## ACTIVE — 10.8-r6

Тема: **зменшення архітектурного ризику великого `main.py` без великого переписування програми**.

### Pre-flight / причина

- `main.py` фактично перевищує 15 000 рядків;
- сам розмір не є runtime-помилкою, але файл одночасно тримає запуск, UI, file-output, частину DB/report сценаріїв і тому підвищує ризик регресій;
- r6 почато від exact immutable r5 source `fc9be91a892ae8be14b04c27b386da120061ec38`;
- правило r6: тільки малий compatibility-preserving refactor, без зміни бізнес-даних і без масового переписування.

### Реалізовано

- створено `output_files.py`;
- з великого `main.py` винесено нейтральні file-output helpers: системне відкриття, report-font candidates, file-access classification, читабельне ім'я копії, locked-file dialog, friendly error, writer-loop;
- у `main.py` лишено тонкий compatibility-wrapper `write_output_file()`, щоб не переписувати всі старі call sites одним кроком;
- `main.APP_VERSION` і `VERSION.txt` піднято до `10.8-r6`;
- додано `tests/test_v10_8_r6.py` з guards на identity, modularization boundary, file-output semantics і START runtime guard;
- одноразовий workflow безпечно переписав тільки цільові top-level functions через AST і після успішної перевірки сам видалився;
- apply run `36771268183` — success;
- refactor commit після one-shot workflow: `e8c765f9d4372801374b2c9ae42ad0f8d1bef027`;
- додано `docs/maintenance/AUDIT_MAIN_MODULARIZATION_v10.8-r6.md` з планом поступової декомпозиції;
- `START.bat` і source-package verification тепер явно вимагають `output_files.py` та `v1085_features.py`.

### Pre-issuance gates

На exact-head `964b6b8ac7ffc0136f410d1057c092c41fee31a2`:

- source package run `36771835142` — success;
- full regression **701/701 OK**;
- Windows PR gate `36771841318` — success;
- macOS PR gate `36771841396` — success, arm64 + x86_64;
- сформовано clean START source artifact `Taxo_v10_8_candidate_r6_START` без nested ZIP і без DB/cache;
- release notes `docs/releases/RELEASE_NOTES_v10.8-r6.md` підготовлено.

### Не змінювалося

- схема робочої БД;
- plan/fact;
- Бланки;
- роль водія;
- СТОІР;
- vehicle documents;
- формат робочого сховища;
- дані користувача.

## DOING

1. Видати immutable fast-test `v10.8-r6` через exact-source publisher.
2. Зафіксувати exact issued SHA, START SHA-256, release і direct download у Issue #61 та PR #109.
3. PR #109 лишити draft/unmerged до окремої команди власника.

## NEXT

Після видачі r6 подальшу декомпозицію робити тільки новою ревізією **10.8-r7**. Наступний безпечний кандидат — backup/migration helpers або attestation query helpers; не змішувати кілька великих доменів в одну ревізію.
