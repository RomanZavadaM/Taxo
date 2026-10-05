# WORKLOG — Taxo

**Оновлено:** 05.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable release:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r10**  
**Latest full multi-platform published checkpoint:** **10.9-r9 / `v10.9-r9`**  
**Current main:** `230eac3cf13cd802a2abbd2456a16ae2a2c01ee0` (після docs PR #133, #134; код = 10.9-r10)  
**Next code revision:** **10.10-r1**  
**Live ledger:** Issue #61

## ACTIVE GOAL — до нового Stable

Ціль власника (05.10.2026): повний аудит → прибирання CI → документація й мовні версії → новий Stable як повний релізний checkpoint.

Повний аудит: [`docs/maintenance/AUDIT_FULL_2026-10-05.md`](docs/maintenance/AUDIT_FULL_2026-10-05.md).

Ключові знахідки:
- **A1 / P0:** у рантаймі шари перезаписують `core.APP_VERSION`; після відкриття вікна програма показує й записує **10.8-r5** (заголовок, «Про програму», PDF-шапки, маніфест backup).
- **C1 / P0:** `publish-v10.3.yml` і `update-release-description-v9.yml` з `contents: write` досі спрацьовують на push у `main` при зміні певних файлів і можуть переписати історичні releases.
- **C2:** 80 workflow, робочих 4; required check — лише `build-windows`; docs-only PR не запускають required check.
- **A4:** PyMuPDF досі обов'язковий для старту (`document_viewer.py`).
- **E:** посібники користувача застарілі (10.4 і раніше).

Регресія на exact `main`: 784 тести, 0 skipped, success (Windows `37052102718`, macOS `37052102799`, START `37052102650`).

## DOING

- Аудит завершено й винесено на рішення власника.

## NEXT

1. **10.10-r1 — CI hardening:** історичні workflow → `docs/history/workflows/`, старі тести → архівний шлях, робочі gates без хардкоду версії, docs-PR gate.
2. **10.10-r2:** A1 (єдине джерело версії + поведінковий тест) і A4 (lazy PyMuPDF).
3. **10.10-r3:** документація й переклади.
4. **Stable checkpoint** — повний реліз.

## BLOCKED — рішення власника

1. Назва Stable-тега і ревізія, з якої він будується.
2. «Мовні пакети»: переклад документації чи локалізація інтерфейсу.
3. Видалення злитих/застарілих гілок (206 шт.; теги/releases не чіпаються).
4. Правило СТОІР ТО-2 → ТО-1.
5. Повна резервна копія за замовчуванням: з документами/сканами чи лише БД з попередженням.

## DONE — 10.9-r10 structural cleanup

PR #132 → main `5e179eabccc35afa984be04208e2e4d96094a2fb`; exact head `ff56519d…` пройшов Windows `37018721703`, Windows 7 `37018721695`, macOS `37018722335`. Docs closeout — PR #133, #134.

## RELEASE STATE

- Stable remains `v10.3` until a separate owner decision.
- Latest already published full multi-platform release remains `v10.9-r9`.
- `10.9-r10` is integrated in `main` and closes the 10.9 revision cycle; not published as a separate release.
- Historical tags/releases are immutable and are not reused.
