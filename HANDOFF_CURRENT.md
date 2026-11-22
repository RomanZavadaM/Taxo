# HANDOFF_CURRENT — Taxo

**22.11.2026 — 10.23-r10 опубліковано як Test prerelease; Stable/Latest лишається 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`, GitHub Latest.

**Current Test:** [10.23-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r10), exact source `f87991c624a971fe3ffd4112e5dfde9fd9e4b6cd`, 8 assets, prerelease. Publisher #45049398522 — SUCCESS.

Exact-source r10 CI: START #45048321322, Windows #45048321299, Win7 #45048321313, macOS Intel/ARM #45048321471 — SUCCESS. Windows і Win7 mandatory Microsoft Defender gates та post-scan integrity verification — SUCCESS.

## Що додає r10

- окремий versioned REVIEW state `taxo.document-import-review.v1`;
- сховище `Data/DocumentLibrary/import_reviews/<batch_id>/review.json` окремо від immutable import batch;
- явні рішення `confirm`, `reject`, `needs_review`;
- confirm звичайної proposal дозволяє тільки точне запропоноване значення;
- ambiguity потребує явного вибору одного з відомих кандидатів;
- рішення жорстко прив'язані до batch + candidate + SHA256 + exact proposal fingerprint;
- stale/tampered review fail-closed;
- рішення атомарно зберігаються та відновлюються після restart;
- `applies_changes=false`: DocumentVault/БД, source, batch і паперовий підпис не змінюються;
- OCR, зовнішній AI/model API, APPLY і фізичні move/rename/delete/copy відсутні.

## Нормативна AI-ready модель

`docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md` — джерело правил: immutable originals, stable identity + metadata + links, staging `INVENTORY → ANALYZE → PROPOSE → REVIEW → APPLY → VERIFY`, confidence/reason/review, import batch + rollback та dry-run перед APPLY.

r6–r10 тепер дають безпечний перед-APPLY цикл: INVENTORY → batch store → verified preview → ANALYZE/PROPOSE → REVIEW. APPLY імпортних пропозицій не починати без окремого рішення власника.

## Наступний крок

Після r10 ревізія переходить на **10.24-r1**.

**10.24-r1 — фундамент модуля «Ділова кореспонденція»** за планом #543:
- окремий доменний модуль, не розростання `main.py`;
- вхідні / вихідні записи з окремими послідовностями номерів;
- stable correspondence ID, дата реєстрації, кореспондент, тема/короткий зміст;
- строк виконання і стан контролю;
- зв'язок «лист ↔ відповідь» та related correspondence;
- зв'язок із готовим документом/DocumentVault без дублювання файла;
- безпечне збереження, backup/restore compatibility і regression-тести.

Перший пакет не робить OCR/AI APPLY і не змінює Stable. UI реєстру будувати поверх цього доменного API, не змішуючи з документним імпортом.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
