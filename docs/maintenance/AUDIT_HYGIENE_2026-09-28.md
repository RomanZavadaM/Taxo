# AUDIT_HYGIENE_2026-09-28 — Taxo

## Мета

Після серії fast-test ревізій 10.6-r4…10.6-r9 виконано окремий аудит цілісності GitHub-стану та службового шуму. Це maintenance-only прибирання: runtime, БД, plan/fact, шляхівки, тахограф, документи ТЗ та видані immutable tags/releases не змінюються.

## Підтверджений стан

- stable: `v10.3` — без змін;
- latest full checkpoint у `main`: `v10.6-r3`;
- latest issued fast-test: `v10.6-r9` → `2705fb5c9105e21bfb669a2d40d4f29449e1a00b`;
- r9 regression: `578/578 OK`;
- clean START verify: `36472489549` — success;
- publisher: `36472783754` — success;
- наступна кодова ревізія: тільки `10.6-r10`.

## Виявлені джерела плутанини

1. `main` закономірно відстає від fast-test лінії: `main` лишається на r3, а r4…r9 живуть у окремій candidate-лінії. Це не runtime-помилка, але нова сесія має читати live ledger і canonical fast-test branch, а не робити висновок лише з `main/WORKLOG.md`.
2. Існує дубльована/тупикова r9-гілка `work/v10.6-r9-vehicle-document-header-responsive`. Канонічна видана лінія — `work/v10.6-r9-vehicle-doc-header-responsive`; дубль не використовувати як базу і не merge.
3. В `.github/workflows` накопичилися історичні one-shot publishers для давно виданих immutable версій. Вони відновлюються з Git history/tag, але в active tree лише захаращують Actions і створюють ризик випадкового ручного запуску.
4. Fast-test лінія r4…r9 має багато дрібних службових commit-ів (publisher identity, cleanup, docs). Це прийнятно для історії candidate, але при наступному повному checkpoint інтеграцію в `main` слід робити через один контрольований PR, не відроджуючи старі work branches.

## Прибирання

З active candidate tree вилучаються тільки історичні release/build workflows, які вже виконали одноразову функцію для виданих immutable версій. Залишаються загальні regression/package gates та workflow, потрібні поточній розробці.

Не видаляються:
- `source-test-archive.yml`;
- актуальні PR regression/build gates;
- файли runtime і regression tests;
- release notes, tags, releases та checksums.

## Правило далі

- один active work branch на одну ревізію;
- після успішного one-shot publisher його workflow видаляється до наступного кроку;
- дублікати branch-name не використовуються;
- r10 починати тільки після цього hygiene checkpoint;
- після issued `10.6-r10` наступна кодова ревізія — `10.7-r1`.
