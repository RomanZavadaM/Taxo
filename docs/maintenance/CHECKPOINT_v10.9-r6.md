# CHECKPOINT — Taxo 10.9-r6

**Статус:** active fast-test slice; не merge у `main` без прямої команди власника.  
**База:** `v10.9-r5` -> `bb2f4424d12cab1fa479950a0743910b909e9fc6`  
**Гілка:** `work/v10.9-r6-personnel-balance-safety`  
**PR:** #125 (draft)

## Scope

Персонал / баланс / П-5 згідно `AUDIT_EXTERNAL_REVIEW_2026-10-01.md`:

1. `Вихідний` / `Відпочинок` не зменшують норму як відпустка або лікарняний.
2. Історичні неявки в driver monthly balance не зводяться до `{driver_id: employee_id}`; вибір виконується по даті та employment period.
3. 2/2 і custom 3/3 закріплені поведінковими тестами.

## Files

- `v1096_personnel_balance.py`
- `feature_layers.py`
- `START.bat`
- `VERSION.txt`
- `tests/test_v10_9_r5.py` — rollover-safe historical test
- `tests/test_v10_9_r6.py`
- `docs/maintenance/AUDIT_PERSONNEL_BALANCE_P5_v10.9-r6.md`
- `docs/releases/RELEASE_NOTES_v10.9-r6.md`

## Safety boundary

- `v10.9-r5` не змінюється;
- схема БД не змінюється;
- stable `v10.3` не змінюється;
- `main` не змінюється;
- до issuance r6 потрібні exact-head regression, START package, platform source gates, checksum та ledger update.
