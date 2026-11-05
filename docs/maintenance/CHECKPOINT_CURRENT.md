# Taxo — поточна контрольна точка

**Дата:** 05.11.2026  
**Stable / Latest:** [Taxo 10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5)  
**Superseded:** `v10.10-r4` — проблема запуску на macOS  
**Rollback:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)  
**Next code revision:** `10.10-r6`  
**Recovery:** `START_HERE.md` → `HANDOFF_CURRENT.md` → private Taxo-profile → live GitHub → `PROJECT_STATE.md`

## Stable 10.10-r5

- Виправлено запуск macOS у навігації «Працівники».
- Власник перевірив виправлення на Apple Silicon Mac mini 04.11.2026.
- Код інтегровано через PR #151.
- Повні збірки Windows, Windows 7, macOS ARM64, macOS Intel і START пройшли успішно.
- Release `v10.10-r5` містить Windows Setup/Portable, Windows 7 Setup/Portable, macOS ARM64/Intel, START і SHA-256.
- Міграцій робочих БД немає.

Release notes: [../releases/RELEASE_NOTES_v10.10-r5.md](../releases/RELEASE_NOTES_v10.10-r5.md).

## Далі

CI optimization лишається окремим етапом. Старий PR #152 не інтегрувати автоматично: спершу звірити його з актуальним `main` r5.
