# AUDIT_HYGIENE_2026-09-28 — Taxo

## Мета

Після серії fast-test ревізій 10.6-r4…10.6-r9 виконано окремий аудит цілісності GitHub-стану та службового шуму. Це maintenance-only аудит: runtime, БД, plan/fact, шляхівки, тахограф, документи ТЗ та видані immutable tags/releases не змінюються.

## Підтверджений стан на момент аудиту

- stable: `v10.3` — без змін;
- latest full checkpoint у `main`: `v10.6-r3`;
- latest issued fast-test: `v10.6-r9` → `2705fb5c9105e21bfb669a2d40d4f29449e1a00b`;
- r9 regression: `578/578 OK`;
- clean START verify: `36472489549` — success;
- publisher: `36472783754` — success;
- наступна кодова ревізія після r9: тільки `10.6-r10`.

## Виявлені джерела плутанини

1. `main` закономірно відстає від fast-test лінії: `main` лишається на r3, а r4…r9 живуть у окремій candidate-лінії. Нова сесія має звіряти live ledger і canonical fast-test branch, а не робити висновок лише з `main/WORKLOG.md`.
2. Існує дубльована/тупикова r9-гілка `work/v10.6-r9-vehicle-document-header-responsive`. Канонічна видана лінія — `work/v10.6-r9-vehicle-doc-header-responsive`; дубль не використовувати як базу і не merge.
3. В `.github/workflows` накопичилися історичні one-shot publisher/build workflows. Початково їх було вилучено з active candidate tree як службовий шум.
4. Після запуску повної regression suite виявлено важливу залежність: частина історичних тестів читає ці workflow-файли як immutable release anchors і перевіряє ними характеристики старих checkpoint-ів. Тому їх видалення порушує regression contract, навіть якщо самі workflow більше не повинні використовуватися для поточної публікації.
5. Fast-test лінія r4…r9 має багато дрібних службових commit-ів. При наступному повному checkpoint інтеграцію в `main` слід робити через один контрольований PR, не відроджуючи старі work branches.

## Корекція після аудиту

Історичні publisher/build workflow **відновлено** в active candidate line як read-only regression/release anchors. Їхня наявність у repository не означає, що старі релізи дозволено перевидавати або пересувати.

Зберігаються:
- `source-test-archive.yml`;
- актуальні regression/package gates;
- історичні workflow, на які прямо спираються regression tests;
- runtime і regression tests;
- release notes, tags, releases та checksums.

Окремі тимчасові one-shot workflow поточної ревізії після виконання видаляються, якщо на них не існує historical regression contract.

## Правило далі

- один active work branch на одну ревізію;
- не видаляти historical release anchors без попередньої перевірки всіх regression references;
- дублікати branch-name не використовувати;
- видані tags/releases не переписувати;
- `10.6-r10` є наступною кодовою ревізією після r9;
- після issued `10.6-r10` наступна кодова ревізія — `10.7-r1`.
