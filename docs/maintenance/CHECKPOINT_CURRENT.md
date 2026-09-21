# Taxo — поточна контрольна точка

**Stable:** Taxo 10.1 · 21.09.2026  
**Stable tag:** `v10.1`  
**Stable target:** `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Previous stable / rollback:** Taxo 10.0  
**Verified candidate before stable:** `v10.1-r5`  
**Candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`

## Статус

Taxo 10.1 — **stable і повністю опублікований**.

## Gate

Ручний Windows UI/navigation gate — **accepted**.

Stable automation:
- source — **162 tests / OK**;
- Windows — **162 tests / OK** + START preflight;
- macOS ARM64 — **162 tests / OK**;
- macOS Intel x86_64 — **162 tests / OK**;
- Windows Setup/Portable — success;
- macOS ARM64/Intel packages — success;
- START/source — success;
- SHA-256 — success;
- GitHub Release `v10.1` — success, 10 assets.

## Політика

- `main` = stable Taxo 10.1;
- `v10.1` = immutable stable;
- `v10.0` = previous stable / rollback;
- `v10.1-r1` … `v10.1-r5` = immutable historical candidates;
- БД/скани/персональні файли у release не входять.

Деталі:
- [Audit 10.1 stable](AUDIT_v10_1_STABLE.md)
- [Release notes 10.1](../releases/RELEASE_NOTES_v10_1.md)
- [Release index](../releases/RELEASE_INDEX.md)
