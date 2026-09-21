# Фінальний аудит Taxo 10.1 stable

**Дата:** 21.09.2026  
**Попередня stable:** Taxo 10.0  
**Verified candidate:** v10.1-r5  
**Candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`  
**Stable target:** `fa5bbe0a5de733af1e227847ef9584daca57676e`

## Рішення

Після ручної Windows-перевірки користувач прямо підтвердив:
- merge у `main`;
- promotion до **Taxo 10.1 stable**;
- Windows x64 Setup/Portable;
- macOS ARM64 та Intel x86_64;
- START/source;
- SHA-256;
- GitHub Release;
- повне оформлення документації.

PR #34 успішно merged у `main`.

## Ручний Windows gate

У r4 було виявлено, що «Звіти» відкривав ще одне повне branded-вікно програми. У r5:
- «Звіти» переведено у головний workspace;
- «Працівники» повертає реєстр;
- детальний табель став single-instance;
- дубльований application sidebar прибрано.

Після повторної перевірки користувач підтвердив stable promotion.

## Candidate gate

v10.1-r5:
- source/START — **157 tests / OK**;
- Windows — **157 tests / OK** + START preflight;
- macOS ARM64 — **157 tests / OK**;
- macOS Intel x86_64 — **157 tests / OK**.

## Stable release gate — завершено

Усі пункти виконані:
1. PR #34 — merged.
2. Stable source verify — **162 tests / OK**.
3. Windows — **162 tests / OK** + START preflight OK.
4. Windows x64 Setup — built and uploaded.
5. Windows x64 Portable — built and uploaded.
6. macOS ARM64 — **162 tests / OK**, Taxo.app built, verified and uploaded.
7. macOS Intel x86_64 — **162 tests / OK**, Taxo.app built, verified and uploaded.
8. START/source — built, verified and uploaded.
9. Per-platform + combined SHA-256 — generated.
10. GitHub Release `v10.1` — published as latest stable.

### Release identity

- tag: `v10.1`;
- target: `fa5bbe0a5de733af1e227847ef9584daca57676e`;
- draft: no;
- prerelease: no;
- assets: **10**;
- previous stable / rollback: `v10.0`.

## Інваріанти

- Plan != Fact;
- exact intervals > duration-only;
- історичні конфлікти не переписуються автоматично;
- П-5 не підставляє план без явного рішення оператора;
- employment state != driver role;
- user DB не входить у Git/release;
- старі tags/releases не пересуваються.

## Після релізу

`main` і `v10.1` є stable source of truth. `v10.0` лишається rollback reference. Candidate releases r1–r5 не пересуваються і не перезаписуються.
