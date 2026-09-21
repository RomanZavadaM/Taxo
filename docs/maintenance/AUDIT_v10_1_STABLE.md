# Фінальний аудит Taxo 10.1 stable

**Дата:** 21.09.2026  
**Попередня stable:** Taxo 10.0  
**Перевірений кандидат:** v10.1-r5  
**Candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`  
**Stable target:** `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Stable tag:** `v10.1`

## Рішення
Після ручної Windows-перевірки користувач прямо підтвердив merge у `main`, promotion до **Taxo 10.1 stable**, multi-platform build, START/source, SHA-256, GitHub Release і документацію.

## Ручний Windows gate
У r4 було виявлено циклічне відкриття повного branded-вікна через «Звіти». У r5 «Звіти» переведено у головний workspace, «Працівники» повертає реєстр, детальний табель став single-instance, а дубльований sidebar прибрано. Після повторної перевірки користувач підтвердив stable promotion.

## Автоматичний candidate gate
- source/START — **157 tests / OK**;
- Windows — **157 tests / OK** + START preflight OK;
- macOS ARM64 — **157 tests / OK**;
- macOS Intel x86_64 — **157 tests / OK**.

## Stable gate — завершено

Stable publisher повторно виконав повний suite вже з `Version: 10.1` і завершився успішно:

- source verify — **162 tests / OK**;
- Windows — **162 tests / OK** + START preflight OK;
- Windows Setup + Portable — success;
- macOS ARM64 — **162 tests / OK** + native Taxo.app;
- macOS Intel x86_64 — **162 tests / OK** + native Taxo.app;
- START/source — success;
- пакети перевірені на відсутність робочих БД/SQLite;
- per-platform та combined SHA-256 — success;
- GitHub Release `v10.1` — published as latest stable;
- release target — `fa5bbe0a5de733af1e227847ef9584daca57676e`.

### Опубліковані артефакти

- `Taxo_v10_1_Setup_Windows_x64.exe`;
- `Taxo_v10_1_Windows_x64_Portable.zip`;
- `Taxo_v10_1_macOS_arm64_Portable.zip`;
- `Taxo_v10_1_macOS_x86_64_Portable.zip`;
- `Taxo_v10_1_START.zip`;
- `SHA256SUMS_v10_1_Windows_x64.txt`;
- `SHA256SUMS_v10_1_macOS_arm64.txt`;
- `SHA256SUMS_v10_1_macOS_x86_64.txt`;
- `SHA256SUMS_v10_1_START.txt`;
- `SHA256SUMS_v10_1.txt`.

### Combined SHA-256

- START: `44ad1f370fa17bfc9f74d7f903fef6a435fb005d535652c7a170e5e055cabeed`;
- Windows Setup: `99ba841e65e25d2d09fa86025b8d52ca72dd0b0c01574b9f6679deb881237f6c`;
- Windows Portable: `782d59867dfdae4e756d6e0ccf8d174316e141a1366d670d66f9150fb1863409`;
- macOS ARM64: `3cd16c3042c45542c52ff3ea758f753f9e98a6866651ddff981c189585ae0927`;
- macOS Intel x86_64: `ee104536088f98ca60b6d0b06f7cd45b127968fe1c19cd1805925da2d1260481`.

## Інваріанти
- Plan != Fact;
- exact intervals > duration-only;
- historical conflicts не переписуються автоматично;
- П-5 не підставляє план без явного рішення оператора;
- employment state != driver role;
- user DB не входить у release;
- старі tags/releases не пересуваються.
