# Taxo 10.9-r10 — structural cleanup

**Дата:** 02.10.2026  
**Статус:** **STABLE** з 05.10.2026 — [GitHub Release v10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10) (Latest); перевірено власником на реальних даних; closes the 10.9 revision cycle  
**Пакети stable:** оригінальні CI-збірки exact head (Windows `37018721703`, Windows 7 `37018721695`, macOS `37018722335`, START `37018715592`), без перезбирання  
**PR:** #132  
**Exact PR head:** `ff56519da35e03204bdaf77f7187cddd692f79d4`  
**Main merge:** `5e179eabccc35afa984be04208e2e4d96094a2fb`

## Зміни

10.9-r10 — структурна ревізія без зміни бізнес-логіки та без міграції робочих даних.

- runtime/support Python modules перенесені в `src/taxo/`;
- root очищений від більшості runtime-модулів;
- runtime templates перенесені в `assets/`;
- active PyInstaller specs та installer definitions перенесені в `packaging/`;
- historical specs перенесені в `packaging/history/`;
- `START.bat`, Windows, Windows 7 і macOS packaging paths адаптовані до нової структури;
- сумісність історичних flat imports збережена bootstrap-механізмом;
- `VERSION.txt` і `main.APP_VERSION` синхронізовані на `10.9-r10`.

## Перевірки exact-head

- Windows: workflow run `37018721703` — success;
- Windows 7 compatibility: `37018721695` — success;
- macOS ARM64/Intel source/build: `37018722335` — success.

## Дані та сумісність

- робочі SQLite-БД не переміщуються і не мігрують;
- backup/workspace paths не змінюються цим refactor;
- скани, кеші та документи користувача не додаються в repository/release;
- структурна зміна стосується source/build layout, а не робочих даних.

## Після r10

Це `r10`, тому цикл 10.9 завершено. За правилами Taxo наступна кодова ревізія — **10.10-r1**. Перехід на `11.x` можливий тільки за прямим рішенням власника.

Stable release лишається `v10.3` до окремого рішення власника. Latest full multi-platform published checkpoint на момент цього closeout — `v10.9-r9`.
