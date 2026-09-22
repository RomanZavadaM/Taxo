# AUDIT — Taxo 10.3 stable

**Дата:** 22.09.2026  
**Verified candidate:** `v10.3-r6`  
**Candidate target:** `619e5995af5982cbf60f7345744789e42463498f`  
**Manual gate:** пройдено користувачем

## Передумови

- r6 merged у `main` через PR #58;
- candidate prerelease `v10.3-r6` опублікований;
- ручний START-тест підтверджено;
- останній main перед promotion має успішні START/source, Windows і macOS runs.

## Stable gate

Stable publisher повинен перевірити stable metadata, виконати full unittest suite на source/Windows/macOS ARM64/macOS Intel, Windows START preflight, зібрати Windows Setup/Portable, macOS ARM64/Intel, clean START/source, перевірити відсутність DB/cache, опублікувати `v10.3` як latest stable і додати SHA-256 manifests.

## Recovery protocol

У stable checkpoint додаються `START_HERE.md`, `WORKLOG.md` і live ledger Issue #61. Нова сесія Taxo відновлює стан з GitHub, а не з пам'яті чату.
