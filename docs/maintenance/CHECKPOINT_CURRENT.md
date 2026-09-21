# Taxo — поточна контрольна точка

**Stable:** Taxo 10.1 · 21.09.2026  
**Previous stable / rollback:** Taxo 10.0  
**Verified candidate:** `v10.1-r5`  
**Stable tag:** `v10.1`  
**Stable target:** `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Verified candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`  
**PR #34:** merged  
**Latest completed candidate:** `10.2-r5` · merged into `main` · prerelease published  
**Next revision:** `10.2-r6`

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
- r4 завершено, опубліковано й злитo в `main`; наступна кодова зміна буде тільки r5.
- Кожен крок завершується прямим посиланням на START-архів без вкладеного ZIP.


## 10.2-r4 завершено

- accepted candidate: `51f84f90c76afde2701a3d26f37e54de279ed2d2`;
- main merge: `71e63f300401eadb7b1f02f376ebd022c9373e7d`;
- GitHub prerelease: `v10.2-r4`;
- START/source gate: success;
- Windows gate: success;
- macOS gate: success;
- наступний кодовий крок: `10.2-r5`.


## 10.2-r5 завершено

- prerelease: `v10.2-r5`;
- candidate target: `fd33f19adf9dc1c2840213d918c9ace52c967f7f`;
- merge у `main`: `2978daecc15e96f109fe2d78de4bde8b9bd0477a`;
- historical `Publish Taxo 10.1 stable` переведено у manual-only режим;
- stable `v10.1` не змінено;
- наступний завершений кодовий крок: `10.2-r6`.
