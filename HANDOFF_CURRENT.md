# HANDOFF_CURRENT — Taxo

**Дата:** 10.11.2026. **Стан:** 10.15-r4 інтегровано; випуск і контрольна документація ще завершуються.

## Підтверджена база

- Stable / Latest: **v10.14-r4**, не змінювати без окремого рішення власника.
- **10.15-r4:** PR [#304](https://github.com/RomanZavadaM/Taxo/pull/304) merged; product main `ae0c673a42c5b633706efdffc1adfd5b1b70681d`. Власник повідомив, що тестував кандидат і він, за його оцінкою, працює.
- Виправлено контроль відсутнього файла документа працівника [#302](https://github.com/RomanZavadaM/Taxo/issues/302); перевірка строку незалежна, дані не змінюються.
- PR-head `f199cdd6adef027788deffe3a9601daf8a87c2f3`: Windows [42807207434](https://github.com/RomanZavadaM/Taxo/actions/runs/42807207434), Win7 [42807207609](https://github.com/RomanZavadaM/Taxo/actions/runs/42807207609), macOS [42807207436](https://github.com/RomanZavadaM/Taxo/actions/runs/42807207436) — SUCCESS.
- Exact-main START [42807804380](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804380), Windows [42807804065](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804065), Win7 [42807804054](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804054), macOS [42807804153](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804153): **результат перевірити у GitHub**. Тег/випуск r4 і їхні файли на момент цього запису **не підтверджені**.
- Перед скороченням описів точні попередні README українською і шістьма мовами, PRODUCT_STATUS, RELEASE_INDEX і PROJECT_STATE збережено й звірено у приватній `dev-strategy/profile/taxo/taxo-history/2026-11-10-before-10.15-r4/`.

## Наступна дія

Перевірити exact-main CI, завершити публікацію кандидатного випуску r4 і перевірити 8 файлів, оновити цей checkpoint, WORKLOG та Issue #61. **До завершення checkpoint не починати наступну кодову ревізію.** Після цього наступна ревізія — **10.15-r5**: узгоджена структурна перебудова з пріоритетом наказів та інструктажів, реальним зменшенням великих файлів і захистом збереження/друку/backup; див. Issue #290. Повнота карти та перевірки backup через UI ще не встановлена.

## Recovery

`START_HERE.md` → `HANDOFF_CURRENT.md` → private `dev-strategy/profile/taxo/TAXO_PROFILE.md` → live GitHub → `PROJECT_STATE.md`.
