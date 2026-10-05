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
- **A4 / P0 (ліцензія):** PyMuPDF — AGPL-3.0 / комерційна Artifex; вшитий у пропрієтарні збірки й обов'язковий для старту. Бланк існує з ранніх версій як DOCX (`python-docx`); PyMuPDF доданий у v8.64 лише для PDF/JPG-штампу, згодом — перегляд PDF і дата №340. Остання опублікована версія без PyMuPDF — `v8.56`. Підлягає повному видаленню в 10.10-r1.
- **E:** посібники користувача застарілі (10.4 і раніше).

Регресія на exact `main`: 784 тести, 0 skipped, success (Windows `37052102718`, macOS `37052102799`, START `37052102650`).

## DOING

- Аудит завершено (PR #135); рішення власника прийняті (див. DECISIONS).
- **10.10-r1 — видалення PyMuPDF** (наступна ревізія за рішенням власника).

## NEXT

1. **10.10-r1 — без PyMuPDF:** PyMuPDF (AGPL-3.0) використовується обмежено — перегляд PDF (`document_viewer.py`), PDF/JPG-штамп бланка (`attestation_render.py`, з v8.64), дата у звіті №340 (`v9_release.py`). Заміна: pypdfium2 + reportlab/pypdf; візуальна регресія бланка й №340; CI-gate проти заборонених залежностей; повні third-party notices.
2. **10.10-r2 — CI hardening:** історичні workflow → `docs/history/workflows/`, старі тести → архівний шлях, робочі gates без хардкоду версії, docs-PR gate, видалення злитих гілок.
3. **10.10-r3:** A1 (єдине джерело версії + поведінковий тест), A5 (попередження «лише БД» у повній резервній копії).
4. **10.10-r4:** документація й переклади.
5. **Stable checkpoint `v10.10`** — повний реліз; bundle без PyMuPDF.

Обмеження до мерджу 10.10-r2: не змінювати в `main` файли `.release/v10.3-stable-ready` і `docs/releases/RELEASE_NOTES_v9_0.md` (тригерять історичні release-workflow).

## DECISIONS — власник, 05.10.2026

1. **Stable:** тег `v10.10`, збирається з фінальної ревізії лінії 10.10-rN після всіх виправлень.
2. **Мовні пакети:** лише документація (посібники українською + переклади README/основних документів на 6 мов). Інтерфейс програми лишається українським.
3. **Гілки:** видалити гілки, повністю злиті в `main`. Теги й releases не чіпаються.
4. **Повна резервна копія за замовчуванням:** лише БД, з явним попередженням, що документи/скани/output не включено (опції включення лишаються).

## BLOCKED

- Правило СТОІР ТО-2 → ТО-1 — відкрите рішення власника; Stable не блокує.
- Історичні releases v8.x–v10.9-r9 містять PyMuPDF — як діяти з уже опублікованими executable-пакетами, вирішує власник (бажано з юридичною консультацією). Stable не блокує.

## DONE — 10.9-r10 structural cleanup

PR #132 → main `5e179eabccc35afa984be04208e2e4d96094a2fb`; exact head `ff56519d…` пройшов Windows `37018721703`, Windows 7 `37018721695`, macOS `37018722335`. Docs closeout — PR #133, #134.

## RELEASE STATE

- Stable remains `v10.3` until a separate owner decision.
- Latest already published full multi-platform release remains `v10.9-r9`.
- `10.9-r10` is integrated in `main` and closes the 10.9 revision cycle; not published as a separate release.
- Historical tags/releases are immutable and are not reused.
