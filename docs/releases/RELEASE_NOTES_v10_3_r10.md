# Taxo 10.3-r10 — Windows 7 compatibility

## Причина

На реальному Windows 7 x64 Taxo 10.3-r9 не запускався ні після інсталяції, ні з Portable. Loader показував відсутній `api-ms-win-core-path-l1-1-0.dll`.

Поточний modern Windows package був зібраний на CPython 3.13 / PyInstaller 6.22.2. Цей runtime не є ціллю для Windows 7.

## Виправлення

- окремий Windows 7 SP1 x64 build на **CPython 3.8.10**;
- legacy-compatible **PyInstaller 5.13.2**;
- окремий `requirements-win7.txt` з версіями бібліотек, що підтримують Python 3.8;
- `release_naming.py` зроблено parse-compatible з Python 3.8;
- інсталятор явно вимагає Windows 7 SP1 або новіше;
- CI перевіряє, що ключові PE-файли не імпортують `api-ms-win-core-path-l1-1-0.dll`.

## Межі

Це compatibility fix без зміни бізнес-логіки, схеми БД чи робочих даних. Modern Windows/macOS packages не замінюються цим legacy build.

Після виданого r10 наступна кодова ревізія — **10.4-r1**.
