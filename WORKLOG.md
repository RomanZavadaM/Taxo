# WORKLOG — Taxo

**Оновлено:** 25.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3`  
**Stable target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`  
**Accepted checkpoint:** `v10.3-r8` → `ac5b22266cdf48ff664a3d13c7e3c3ec86876cfc`  
**r8 manual gate:** accepted by owner  
**Active candidate:** `10.3-r9`  
**Branch:** `work/v10.3-r9-main-checkpoint`  
**PR:** pending  
**Live ledger:** Issue #61.

## ACTIVE SLICE — 10.3-r9

### Ціль
Виконати команду власника «дописуй, доробляй, зливай в main» як повний релізний checkpoint згідно з `PROJECT_RULES.md`.

r8 уже був виданий як immutable START prerelease, тому повний multi-platform checkpoint отримує наступну ревізію `10.3-r9`.

### Scope
- без нової бізнес-логіки відносно прийнятого r8;
- Windows x64 Setup + Portable;
- macOS ARM64 + Intel x86_64 Portable;
- START/source;
- per-platform + combined SHA-256;
- legal notices у source та executable packages;
- immutable `v10.3-r9`;
- merge PR у `main`;
- синхронізація PROJECT_STATE / WORKLOG / checkpoint / release index / Issue #61.

### Критерії готовності
- `main.APP_VERSION == VERSION.txt == 10.3-r9`;
- historical r8 regression не блокує наступний revision;
- source regression зелений;
- Windows package build + regression + START preflight зелені;
- macOS ARM64 та Intel package builds/regression зелені;
- release має 5 основних пакетів + checksum manifests;
- PR merged у `main`;
- stable `v10.3` не пересувається.

## DOING

- [x] r8 manual gate accepted.
- [x] Створено `work/v10.3-r9-main-checkpoint`.
- [x] Версію піднято до `10.3-r9`.
- [x] Historical r8 identity test відв’язано від active candidate version.
- [x] Додано r9 Windows installer spec.
- [x] Додано r9 macOS bundle spec із legal notices.
- [x] Додано r9 regression і release notes.
- [ ] Додати full multi-platform publisher.
- [ ] Відкрити PR.
- [ ] Пройти exact-head source/Windows/macOS gates.
- [ ] Перевірити tag/release/assets.
- [ ] Merge у `main`.
- [ ] Фінально синхронізувати документацію та ledger.

## NEXT

Додати full r9 publisher, відкрити PR, потім запустити exact-head release gate.

## BLOCKED

Немає.
