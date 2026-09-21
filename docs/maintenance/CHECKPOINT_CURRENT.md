# Taxo — поточна контрольна точка

**Stable:** Taxo 10.1 · 21.09.2026  
**Previous stable / rollback:** Taxo 10.0  
**Verified candidate:** `v10.1-r5`  
**Stable tag:** `v10.1`  
**Stable target:** `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Verified candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`  
**PR #34:** merged  
**Active development:** `10.2-r4` · `work/v10.2-r4-replanning` · PR #40

## Gate

Manual Windows gate — **accepted**.

Candidate automation:
- source/START — **157 tests / OK**;
- Windows — **157 tests / OK** + START preflight;
- macOS ARM64 — **157 tests / OK**;
- macOS Intel x86_64 — **157 tests / OK**.

## Stable result

Версію переведено з `10.1-r5` у **10.1 stable**. PR #34 злитий у `main`; stable publisher завершився успішно.

- source verify — **162 tests / OK**;
- Windows — **162 tests / OK** + START preflight; Setup + Portable published;
- macOS ARM64 — **162 tests / OK**; package published;
- macOS Intel x86_64 — **162 tests / OK**; package published;
- START/source — published;
- per-platform + combined SHA-256 — published;
- GitHub Release `v10.1` — latest stable.

## Політика

- `v10.0` та `v10.1-r1` … `v10.1-r5` — immutable;
- `v10.1` створено stable publisher з commit у `main` і тепер є immutable stable;
- БД/скани/персональні файли у release не входять.


## Поточний candidate workflow

- Кожен завершений крок = нова ревізія.
- `r1 ... r10`; після `r10` — наступна minor-версія з `r1`.
- r4 є окремим тестовим станом; наступна зміна після виданого r4-архіву буде вже r5.
- Кожен крок завершується прямим посиланням на START-архів без вкладеного ZIP.
