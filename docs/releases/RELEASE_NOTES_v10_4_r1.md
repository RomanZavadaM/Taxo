# Taxo 10.4-r1 — full multi-platform checkpoint with Windows 7

## Статус

10.4-r1 — повний релізний checkpoint після прийнятого користувачем Windows 7 compatibility fix 10.3-r10.

10.3-r10 вже був виданий як immutable prerelease, тому згідно з правилом ревізій наступний повний checkpoint переходить на **10.4-r1**.

## Що входить

- Windows x64 modern Setup;
- Windows x64 modern Portable;
- Windows 7 SP1 x64 Setup;
- Windows 7 SP1 x64 Portable;
- macOS ARM64 Portable;
- macOS Intel x86_64 Portable;
- START/source;
- per-platform SHA-256 і combined manifest;
- LICENSE.md, COPYRIGHT.md та THIRD_PARTY_NOTICES.md у пакетах.

## Windows 7

Початковий modern package 10.3-r9 не запускався на Windows 7 через loader error:
`api-ms-win-core-path-l1-1-0.dll`.

Compatibility line використовує:
- CPython 3.8.10 x64;
- PyInstaller 5.13.2;
- Python-3.8-compatible dependency pins;
- dedicated `Taxo_win7.spec`;
- installer minimum `Windows 7 SP1`;
- PE import regression для exact failing DLL.

Власник перевірив Portable 10.3-r10 на реальному Windows 7 x64 — **успішний запуск підтверджено**.

## Межі змін

- нової бізнес-логіки відносно прийнятого 10.3-r10 немає;
- схема БД не змінюється;
- робочі БД, скани, документи користувача та кеші в release не входять;
- stable `v10.3` лишається immutable rollback/stable checkpoint;
- після виданого 10.4-r1 наступний кодовий крок — **10.4-r2**.
