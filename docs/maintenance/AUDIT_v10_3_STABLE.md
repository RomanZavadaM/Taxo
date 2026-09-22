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

## Stable result

Stable source target: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.

GitHub Actions run `35764396010` завершився **success**:
- verify-source — success;
- build-windows — success;
- build-start — success;
- macOS x86_64 — success;
- macOS arm64 — success;
- publish — success.

Опубліковано `v10.3` з Windows Setup/Portable, macOS ARM64/Intel, clean START/source і SHA-256 manifests. Release містить 10 assets. Робочі БД/cache не входять у пакети.

## Recovery protocol

У stable checkpoint додаються `START_HERE.md`, `WORKLOG.md` і live ledger Issue #61. Нова сесія Taxo відновлює стан з GitHub, а не з пам'яті чату.
