# Індекс релізів Taxo

**Стан:** 30.09.2026  
**Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — immutable  
**Latest full multi-platform checkpoint:** [Taxo 10.8-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.8-r3)  
**Latest integrated code checkpoint in `main`:** Taxo **10.8-r3** — merged via PR #105  
**Next code revision:** **10.8-r4**.

> `v10.3` лишається stable до окремого рішення власника. `v10.8-r3` — поточний інтегрований і повний multi-platform checkpoint; це не автоматичне stable promotion.

## Поточний checkpoint

| Ревізія | Main / issued source | Перевірка | Пакети / зміст |
|---|---|---|---|
| **10.8-r3** | main merge `db444a37ead421c8083558cfcf81ee97adc241f6`; tag source `d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd` | publisher `36737140249`; full package `36741933852` — success | Windows x64 Setup/Portable, Windows 7 SP1 x64 Setup/Portable + PE gate, macOS ARM64/Intel, START, platform/full SHA-256; ТЦК date fix + optional vehicle requisites |

START: `Taxo_v10_8_candidate_r3_START.zip`  
SHA-256: `aa75661658194425f7dc95c353516a6f1c44f98040989f72d402985e2f023d00`

## Taxo 10.8 history

| Ревізія | Issued source | Статус | Зміст |
|---|---|---|---|
| **10.8-r3** | `d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd` | **full multi-platform checkpoint; PR #105 merged** | виправлення дати відомості ТЦК; реквізити ТЦК у картці ТЗ |
| 10.8-r2 | immutable issued checkpoint | fast-test | runtime Tk/ttk UI smoke tests під Xvfb; контроль видимості та invoke критичних дій |
| 10.8-r1 | immutable issued checkpoint | fast-test | functionality-contract guard інтерфейсу та повернення видимих дій документів ТЗ |

## Останні повні multi-platform checkpoints

| Tag | Статус | Пакети |
|---|---|---|
| [v10.8-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.8-r3) | **Latest full multi-platform checkpoint** | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, platform/full SHA-256 |
| [v10.6-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r10) | previous full checkpoint | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, platform/full SHA-256 |
| [v10.6-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3) | historical | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, SHA-256 |
| [v10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8) | historical | Windows x64/Win7, macOS ARM64/Intel, START, SHA-256 |
| [v10.4-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r2) | historical | Windows x64/Win7, macOS ARM64/Intel, START, SHA-256 |

## Historical identity anchors

- **Taxo 10.6-r10** — issued source `0baad010d0c0d4f29db62f26c29d512c71058928`; попередній повний інтегрований checkpoint.
- **Taxo 10.4-r7** — historical issued source `9f397a092fe828570927bc39cef7a3a467e2aff0`; межа між локальним контролем документів ТЗ та державними реєстрами.
- Історичні anchors зберігаються для regression/history і не використовуються як нова кодова база.

## Stable line

| Tag | Статус |
|---|---|
| [v10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) | **Current stable** |
| [v10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1) | Previous stable / rollback |
| [v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0) | Historical stable |
| [v9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1) | Historical stable |

## Документи поточної лінії

- [Release notes 10.8-r3](RELEASE_NOTES_v10.8-r3.md)
- [Release notes 10.8-r2](RELEASE_NOTES_v10.8-r2.md)
- [Release notes 10.8-r1](RELEASE_NOTES_v10.8-r1.md)
- [Release notes 10.6-r10](RELEASE_NOTES_v10.6-r10.md)

Точна історія старіших revisions збережена в Git history, release notes та Issue #61. Старі work/candidate branches не використовуються як нова кодова база.

## Release policy

1. Stable формується тільки після manual operational gate та окремого рішення власника.
2. Виданий tag/release не пересувається і не перевидається поверх іншого коду.
3. Full multi-platform checkpoint містить Windows, Windows 7 compatibility packages, macOS packages, START та checksums.
4. БД, SQLite, скани, кеші та персональні документи не публікуються.
5. Кодові зміни йдуть через окрему work branch і PR.
6. «Злити у main» = перевірки → інтеграція → синхронізація документації → повні пакети/checksums, якщо не вказано інше.
