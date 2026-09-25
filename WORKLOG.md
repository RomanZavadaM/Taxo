# WORKLOG — Taxo

**Оновлено:** 25.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3`  
**Latest full checkpoint:** `v10.3-r9` → `9268f9a94d48388238ac957ee7c32071e887da2b`  
**Published candidate:** `v10.3-r10` → `b9e3d122728c4043a1e7ec9e0a85ece949d14d38`  
**Active branch:** `work/v10.3-r10-windows7-compat`  
**Problem reproduced:** Windows 7 x64 loader error `api-ms-win-core-path-l1-1-0.dll`  
**Publisher run:** `36110712792` — success  
**Live ledger:** Issue #61.

## ACTIVE SLICE — 10.3-r10 Windows 7 compatibility

### Реалізовано
- CPython 3.8.10 x64 compatibility build;
- PyInstaller 5.13.2;
- Python-3.8-compatible dependency pins;
- окремий `Taxo_win7.spec`;
- Windows 7 SP1 installer minimum;
- Python 3.8 regression suite: **287 tests / OK**;
- Win7 Portable build: success;
- PE import scan: success, exact failing `api-ms-win-core-path-l1-1-0.dll` не імпортується;
- Win7 Setup build: success;
- START + SHA-256: success;
- immutable prerelease `v10.3-r10` published.

### Manual gate — PENDING
Потрібен реальний запуск на Windows 7 SP1 x64:
1. Portable → `Taxo.exe`;
2. Setup → встановлення → запуск;
3. перевірити, що немає loader/DLL error і відкривається головне вікно.

До успішного manual gate **не зливати r10 у main**.

## NEXT

Користувач тестує `v10.3-r10` на тому самому Windows 7. Якщо запускається — прийняти manual gate і завершити merge/documentation. Якщо ні — зафіксувати точний новий loader/runtime error; наступна кодова зміна після вже виданого r10 буде тільки **10.4-r1**.

## BLOCKED

Manual Windows 7 gate.
