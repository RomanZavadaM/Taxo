# HANDOFF_CURRENT — Taxo

**Оновлено:** 05.11.2026

## База
- Repository: `RomanZavadaM/Taxo`
- `10.10-r5` уже інтегрована в `main`.
- Попередній stable: `v10.10-r4` — має підтверджену проблему запуску на macOS.
- Rollback: `v10.9-r10`.
- Private profile: `RomanZavadaM/dev-strategy` / `profile/taxo` / `TAXO_PROFILE.md`.

## Що зроблено
- Виправлено аварійний запуск macOS у навігації «Працівники».
- Власник 04.11.2026 перевірив виправлення на Apple Silicon Mac mini.
- Офіційна ревізія — `10.10-r5`; видану r4 не перевикористано.
- PR #151 інтегровано в `main`.
- Повна перевірка вже на `main`: Windows, Windows 7, macOS ARM64, macOS Intel і START — успішно.
- PR #152 з оптимізацією перевірок лишається окремою роботою.

## Єдина наступна дія
Опублікувати повний комплект `v10.10-r5` з перевірених збірок і зробити його новою stable/Latest замість `v10.10-r4`. Після цього синхронізувати README, PROJECT_STATE, release index і резервну документацію.

## Recovery
`START_HERE.md` → цей HANDOFF → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
