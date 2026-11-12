# HANDOFF_CURRENT — Taxo

**12.11.2026 — Stable / Latest: v10.17-r10 (ПІДТВЕРДЖЕНО). Наступна кодова ревізія — 10.18-r1.**

## Підтверджена база

- **Нова Stable/Latest: [v10.17-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.17-r10)**, immutable exact source `6536a6da6cade49229fa1944e2aa47f941df40a6`. Owner approval 12.11.2026. Повний випуск створено штатним guarded workflow [43271144404](https://github.com/RomanZavadaM/Taxo/actions/runs/43271144404) **SUCCESS**; GitHub `releases/latest` підтвердив `v10.17-r10`, `prerelease=false`, `draft=false`, **8 assets** (2 Windows Setup, 4 portable Windows/Win7/macOS Intel/ARM, START, SHA256). Git tag на exact source, релізні файли доступні зі стандартної сторінки Releases.
- **Стара Stable/rollback: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, exact source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`, незмінна, 8 assets збережені.
- Код r10 інтегровано в `main` через [PR #378](https://github.com/RomanZavadaM/Taxo/pull/378), merge `bf20d20f1e0ac76317544562137d004e5303bee1`. Перед інтеграцією exact-source START/source [43267826061](https://github.com/RomanZavadaM/Taxo/actions/runs/43267826061) **SUCCESS, 1205 tests**, Windows [43267844221](https://github.com/RomanZavadaM/Taxo/actions/runs/43267844221), Win7 [43267845707](https://github.com/RomanZavadaM/Taxo/actions/runs/43267845707), macOS Intel/ARM [43267844237](https://github.com/RomanZavadaM/Taxo/actions/runs/43267844237) — усі **SUCCESS**. Після синхронізації з `main` CI для merge-head `8cd4aba2490433df72c098dae8858287eb5c38b5` також пройшли на усіх трьох платформних workflows.
- Релізний marker PR [#380](https://github.com/RomanZavadaM/Taxo/pull/380) merged `273ccf89badb777dcffe636f4e62f3a8d2e47e5c`; запустив guarded stable publisher, загальний publisher коректно пропущено через `[skip-publish]`. Release/build/security workflow не змінювали.
- Накопичувальна r1…r10: сортування ТЗ, маршрутів, працівників, наказів, водіїв, історії наказу; виходи «Закрити»/«Скасувати» у відповідних діалогах; безпечні редактори тахографа і маршрутів, додаткові підтвердження перед destructive actions.
- **Не прийнято вручну:** Windows DPI 100/125/150 %, фокус/табуляція, X із незбереженою чернеткою та повторне відкриття. Автоматичні тести не замінюють ручної перевірки.
- Власник відклав бібліотеку шаблонів та сховище документів. Не чіпати до окремої команди. Продовжувати модульний, читабельний код, не зменшувати рядки заради метрики.
- Нове правило: після кожної `r5` і `r10` автоматично публікувати тестовий GitHub Pre-release з усіма portable. Команда «зливаємо» — повний Stable із Windows installers, portable, START, checksums.

## Одна наступна дія

**Почати 10.18-r1** від перевіреної бази `main`, продовжувати `docs/maintenance/UI_NAVIGATION_CONSISTENCY_AUDIT_2026-11-12.md`: інші робочі реєстри, службові Toplevel, доступність виходу, X/незбережені дані/повторне відкриття, вибір рядків після сортування. До зміни коду виконати recovery preflight за правилами проєкту. Ручний Windows UI/DPI gate залишити явно pending.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile `RomanZavadaM/dev-strategy:profile/taxo/TAXO_PROFILE.md` → live GitHub PR/CI/releases → `PROJECT_RULES.md` та `PROJECT_STATE.md`.
