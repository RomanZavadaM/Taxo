# HANDOFF_CURRENT — Taxo

**Оновлено:** 05.11.2026

## База
- Repository: `RomanZavadaM/Taxo`
- Stable / Latest: **`v10.10-r5`**
- Superseded: `v10.10-r4` — підтверджена проблема запуску на macOS
- Rollback: `v10.9-r10`
- Наступна кодова ревізія: **10.10-r6**
- Private profile: `RomanZavadaM/dev-strategy` / `profile/taxo` / `TAXO_PROFILE.md`

## Завершено
- Виправлено аварійний запуск macOS у навігації «Працівники».
- Власник 04.11.2026 перевірив виправлення на Apple Silicon Mac mini.
- PR #151 інтегровано в `main`.
- Повний контроль на `main`: Windows, Windows 7, macOS ARM64, macOS Intel і START — успішно.
- `v10.10-r5` опублікований повним комплектом із 8 файлів.
- Поточний stable переводиться на `v10.10-r5`; r4 лишається історичною й не використовується як Mac-збірка.
- PR #152 з оптимізацією перевірок не змішувався з r5.

## Єдина наступна дія
Після підтвердження stable-promotion `v10.10-r5` повернутися до CI optimization: PR #152 не зливати як є, а спочатку звірити його з новим `main` r5 і перенести корисні зміни на актуальну базу.

## Recovery
`START_HERE.md` → цей HANDOFF → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
