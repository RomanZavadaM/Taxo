# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 15.11.2026.**

- Завершений product checkpoint: **10.20-r1** (PR #446).
- Exact product/release source SHA: `f80a1e583f896f4d0d8f63265e7ab0aadb657185`.
- Test prerelease [v10.20-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r1), publisher `43762135252` SUCCESS; 4 portable + START + SHA256.
- Release-trigger PR #447 merged as `9fc246f335da4c3853e891a219fc7fdc8d839f6a`.
- Stable/Latest: **v10.18-r3**, unchanged.

## Функціональний результат

10.20-r1 розширює prepared DOCX → PDF/preview/print: підтримувані inline-зображення з exact контрольованої Word-редакції тепер переносяться у PDF, у тому числі всередині клітинок таблиць. Порядок text/image зберігається на рівні абзацу, базове вирівнювання береться з Word paragraph.

Зображення нормалізуються через чинний Pillow; нових runtime dependencies немає. Є limits на кількість/розмір/pixels. Зовнішні image links не завантажуються.

Unsupported layout лишається fail-closed: floating drawings, VML/legacy pictures, header/footer drawings, nested/складні таблиці. PDF не змінює DOCX, revision history чи document/signature/business status.

## CI та security gates

Exact-main product SHA `f80a1e583f896f4d0d8f63265e7ab0aadb657185`: START/source `43761081149` — 1369/1369 SUCCESS; Windows `43761081164`, Win7 `43761081155`, macOS Intel/ARM `43761081179` — SUCCESS. Windows/Win7 Defender та post-scan integrity PASS. Publisher `43762135252` SUCCESS; immutable release target — exact product SHA, 6 assets. GitHub Latest/Stable — v10.18-r3.

## Наступна ревізія

**10.20-r2** — DocumentVault core як окремий модуль: базова структура сховища та реєстру готових/архівних документів із provenance-посиланням на конкретну prepared-редакцію.

У цей slice не змішувати:
- auto-migration чинних PaperDocuments;
- scans/originals;
- digital signature / підписні докази;
- автоматичний статус «підписано»;
- розширення складного Word-layout renderer.

## Recovery

Читати START_HERE.md → HANDOFF_CURRENT.md → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; `WORKLOG.md` — історія.

Через повторні input-stream обриви цієї сесії наступний великий slice починати у новому чаті після recovery.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
