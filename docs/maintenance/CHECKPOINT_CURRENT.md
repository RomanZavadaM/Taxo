# Поточна контрольна точка Taxo

**20.11.2026 — Stable/Latest 10.23-r4.**

- Release: [v10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4)
- Exact source: `a919ced6bc8665ced70ebb4d897808e4e2618667`
- 8 канонічних assets; tag target незмінний.
- START #44803423646 — SUCCESS.
- Windows #44803423874 — SUCCESS, Defender/integrity PASS.
- Windows 7 #44803423649 — SUCCESS, Defender/integrity PASS.
- macOS Intel/ARM #44803423740 — SUCCESS.
- Test publisher #44804999191 — SUCCESS.
- Власник вручну підтвердив працездатність r4 20.11.2026.
- Stable promotion #44811800328 — SUCCESS; `releases/latest` = v10.23-r4; prerelease=false.

**Поточний Test:** v10.23-r5, exact source `dc5dcaa3aa86b4d42cfdec8019fbc73c73f2be3a`, 8 assets, publisher #44927558482 SUCCESS. **Stable/Latest:** v10.23-r4. v10.23-r3 навмисно не видавався.

r4 включає адаптивний перегляд наказів у вузькому вікні, зміни r2/r3 для учасників наказів і регульованих документних робочих областей, а також 37 strict live UI routes.

r5 інтегрована й опублікована як Test. Наступний кодовий крок: **10.23-r6** — inventory/dry-run core для існуючої бази документів відповідно до `docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md`. На r6 заборонено фізичне move/rename/delete та автоматичний APPLY: тільки inventory, SHA256, manifest, exact duplicates і звіт. #553/#556/#562 не закривати автоматично; draft #543/#395 лишити історичними design-гілками.

Актуальний стан: [PROJECT_STATE](../../PROJECT_STATE.md) · [HANDOFF](../../HANDOFF_CURRENT.md) · [WORKLOG](../../WORKLOG.md).
