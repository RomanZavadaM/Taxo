# Taxo 10.18-r9 — Windows binary security checkpoint

## Призначення

`10.18-r9` — **security/build-only test candidate**. Функціональність Taxo від `10.18-r8` не розширюється. Stable/Latest `v10.18-r3` не змінюється.

Причина checkpoint: Firefox заблокував завантаження Windows artifact r8 загальним попередженням про можливе шкідливе ПЗ. Назву детекції або конкретний антивірусний verdict отримано не було, тому r8 executable release залишився на SECURITY HOLD.

## Що встановлено контрольним порівнянням r8

- exact-source та integration Windows builds мали однаковий набір 1116 файлів у Portable;
- продуктова різниця між відповідними source refs стосувалася лише recovery-документації;
- `Taxo.exe` в обох збірках мав однаковий розмір; побайтово відрізнялися лише 6 байтів, пов'язаних із PE build timestamp / checksum;
- в actual PyInstaller r8 log не зафіксовано запуску UPX, тому `upx=True` не вважається доведеною причиною Firefox warning;
- різні хеші свіжих unsigned builds можуть впливати на reputation/heuristics, але це **не є доказом false positive і не є доказом безпечності**.

## Зміни r9

- `packaging/Taxo.spec`: UPX явно вимкнено, щоб майбутня зміна runner/tool availability не могла непомітно змінити спосіб пакування;
- додано окремий CI-only `scripts/windows_malware_gate.ps1`; він не запускає Taxo та виконує Microsoft Defender custom scan із актуалізацією сигнатур;
- Defender gate є fail-closed: якщо scanner недоступний, update/scan завершується помилкою або є detection — Windows artifact не завантажується;
- scan виконується без remediation, після чого SHA-256 Portable та Setup повторно звіряються з manifest;
- додається build provenance: exact Git head, runner, Python, PyInstaller, `pip freeze`, SHA-256 spec;
- GitHub Actions artifacts отримують унікальне ім'я з `run ID` замість повторюваного `Taxo-current-Windows-x64`; версія лишається в канонічних іменах ZIP/EXE всередині artifact;
- додано regression contract, який фіксує security gate та порядок upload.

## Межі приймання

- PASS Microsoft Defender gate — це один необхідний контроль, але не універсальна гарантія від усіх malware engines;
- якщо Firefox або інший vendor продовжує блокувати r9, executable не публікувати як GitHub Release до встановлення конкретного verdict/репутаційної причини;
- code signing у цьому checkpoint не додається без окремо підготовленого сертифіката й процесу захисту ключа;
- `v10.18-r3` лишається Stable/Latest до окремого рішення власника.
