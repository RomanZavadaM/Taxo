# Поточна контрольна точка Taxo

**21.11.2026 — Stable/Latest 10.23-r4; Current Test 10.23-r5.**

## Stable

- Release: [v10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4)
- Exact source: `a919ced6bc8665ced70ebb4d897808e4e2618667`
- 8 assets; owner manual acceptance 20.11.2026; stable promotion #44811800328 SUCCESS.
- 37 strict live UI routes.

## Test

- Release: [v10.23-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r5)
- Exact source: `dc5dcaa3aa86b4d42cfdec8019fbc73c73f2be3a`
- 8 assets; prerelease; publisher #44927558482 SUCCESS.
- START #44926983535, Windows #44926983543, Win7 #44926983541, macOS Intel/ARM #44926983524 — SUCCESS; Defender/integrity PASS.
- «Документи → Каталог» перевірено для 760×470; 38-й strict route `documents.catalog_small_viewport`.
- Stable/Latest не змінено.

## Наступний напрям

Нормативна AI-ready модель збереження/класифікації підготовлена у draft PR #580. Після recovery r5 її треба інтегрувати, після чого наступний вузький кодовий крок — **10.23-r6 read-only inventory існуючого архіву**: regular files, relative path/name, size, MIME, mtime, streaming SHA256, exact duplicate groups, versioned manifest/import_batch. Без OCR/AI/move/delete у першому кроці.

#553/#556/#562 не закривати автоматично; draft #543/#395 не чіпати.

Актуальний стан: [PROJECT_STATE](../../PROJECT_STATE.md) · [HANDOFF](../../HANDOFF_CURRENT.md) · [WORKLOG](../../WORKLOG.md).
