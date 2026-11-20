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

**Попередня Stable:** v10.23-r1. **Новішого Test немає.** v10.23-r3 навмисно не видавався.

r4 включає адаптивний перегляд наказів у вузькому вікні, зміни r2/r3 для учасників наказів і регульованих документних робочих областей, а також 37 strict live UI routes.

Активний кодовий крок: **10.23-r5**, PR #576, head `ef1c9d543a8dce0fc902cbe8a36dffa1fc01e291` — один пов'язаний пакет малого viewport «Документи → Каталог». START уже SUCCESS; інші exact-head checks на момент аудиту ще виконуються. Не merge/не публікувати до повного зеленого набору. Stable лишається r4. #553/#556/#562 не закривати автоматично; draft #543/#395 не чіпати.

Актуальний стан: [PROJECT_STATE](../../PROJECT_STATE.md) · [HANDOFF](../../HANDOFF_CURRENT.md) · [WORKLOG](../../WORKLOG.md).
