# Taxo — поточна контрольна точка

**Stable promotion:** Taxo 10.1 · 21.09.2026  
**Previous stable / rollback:** Taxo 10.0  
**Verified candidate:** `v10.1-r5`  
**Candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`  
**Work branch:** `work/v10.1-driver-role-ui-refresh`  
**PR:** #34

## Gate

Manual Windows gate — **accepted**.

Candidate automation:
- source/START — **157 tests / OK**;
- Windows — **157 tests / OK** + START preflight;
- macOS ARM64 — **157 tests / OK**;
- macOS Intel x86_64 — **157 tests / OK**.

## Stable promotion

Версію переведено з `10.1-r5` у `10.1`. Перед merge PR проходить повторний CI зі stable metadata. Після green PR #34 зливається у `main`, де `Publish Taxo 10.1 stable` збирає та публікує всі офіційні пакети.

## Політика

- `v10.0` та `v10.1-r1` … `v10.1-r5` — immutable;
- `v10.1` створюється тільки stable publisher з merge commit у `main`;
- БД/скани/персональні файли у release не входять.
