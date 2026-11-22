# PROJECT_STATE — Taxo

**Підтверджено GitHub 22.11.2026 після публікації Test 10.24-r2.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`.

**Current Test:** [10.24-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r2), exact source `d07f26d8e9e9db6d33278cac5a0199e2d8ae4b50`, 8 assets, prerelease. Publisher #45064537526 — SUCCESS.

## Stable r4

Stable r4 залишається вручну прийнятою власником версією. 37 strict live UI routes; Stable не змінюється без окремого рішення власника.

## Current Test 10.24-r2

Лінія ділової кореспонденції:
- r1: incoming/outgoing registry, independent annual numbering, semantic dates, correspondent/control metadata, response/related links, stable document_ref, full backup/restore;
- r2: controlled immutable attachments або live DocumentVault link, SHA256/MIME/size/name metadata, content-addressed dedupe, history-only removal, content/integrity guards і full backup/restore;
- attachment не означає sent/received/delivered/signed і не переписує registry state.

Exact-source CI `d07f26d8e9e9db6d33278cac5a0199e2d8ae4b50`: START #45063475205, Windows #45063475214, Win7 #45063475185, macOS Intel/ARM #45063475161 — SUCCESS; Windows/Win7 Defender + post-scan integrity PASS. Guarded trigger PR #613 merged as `14a280f865ec789e14fdc1ff83602925618ba854`; publisher #45064537526 — SUCCESS.

## Наступна ревізія

**10.24-r3:** відповіді, справи та контроль строків: explicit state transitions, окрема фактична відправка outgoing, due/overdue, safe reply creation, logical case/thread, append-only history та backup/restore. UI — наступним окремим пакетом поверх доменних API. Без e-mail automation, OCR/AI APPLY або physical purge.

AI-ready document import r6–r10 завершений на REVIEW без APPLY. APPLY — лише після окремого рішення власника.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
