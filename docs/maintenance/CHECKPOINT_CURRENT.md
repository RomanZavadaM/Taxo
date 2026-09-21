# Taxo — поточна контрольна точка

**Stable:** Taxo 10.1 · 21.09.2026  
**Previous stable / rollback:** Taxo 10.0  
**Verified candidate:** `v10.1-r5`  
**Stable tag:** `v10.1`  
**Stable target:** `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Verified candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`  
**PR #34:** merged  
**Latest completed candidate:** `10.2-r7` · PR #45 merged · prerelease published  
**Accepted candidate target:** `b5aa0f3c213988fe51c2a98414b4acd3db70e710`  
**Main merge:** `e272c8794b8df17dd3ec2e64a811c707158c94a0`  
**Next code revision:** `10.2-r8`

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


## 10.2-r5 у роботі

- прибирається автозапуск historical `Publish Taxo 10.1 stable` від push у `main`;
- stable `v10.1` не змінюється;
- regression gate перевіряє manual-only trigger;
- після r5 наступна ревізія — r6.


## 10.2-r6 — candidate ready for manual UI test

- secondary-window UI consistency;
- 12 великих службових/звітних вікон переходять на approved branding;
- schema/data/business logic unchanged;
- regression gate: 201 tests / OK на source, Windows, macOS ARM64 та Intel;
- Windows START preflight: OK;
- після виданого r6 наступний крок — тільки 10.2-r7.


## 10.2-r7 завершено

- approved secondary-window UI збережено;
- r6 не переписувався;
- опубліковано правильний пакет `Taxo_v10_2_candidate_r7_START.zip`;
- Windows і macOS PR-gates пройшли успішно;
- PR #45 merged;
- candidate target: `b5aa0f3c213988fe51c2a98414b4acd3db70e710`;
- main merge: `e272c8794b8df17dd3ec2e64a811c707158c94a0`;
- наступний кодовий revision — `10.2-r8`.
