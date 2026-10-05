# Архів одноразових GitHub Actions workflow

Ці workflow використовувались для публікації/застосування конкретних історичних ревізій Taxo (v9.0 … v10.9) і **більше не виконуються**: GitHub запускає лише файли з `.github/workflows/`.

Архівовано в 10.10-r2 (аудит 05.10.2026, знахідка C1/C2):
- усі мали `contents: write`, а `publish-v10.3.yml` і `update-release-description-v9.yml` досі спрацьовували на push у `main` і могли переписати історичні releases;
- історичні теги й releases незмінні — архів зберігається лише для аудиту та історичних regression-тестів.

Історичні тести читають ці файли за старими шляхами: `tests/stage_legacy_layout.py` копіює їх у `.github/workflows/` **лише в робочій копії CI** перед запуском тестів (не комітиться і не виконується GitHub).

Активні gates (у `.github/workflows/`):
- `build-windows-v8.70.yml` — регресія + Windows x64 Portable/Setup (required check `build-windows`, усі PR);
- `build-win7-current.yml` — Windows 7 SP1 x64 Portable;
- `build-macos-v8.70.yml` — macOS arm64 / x86_64;
- `source-test-archive.yml` — регресія на Linux + START-архів.

Нові одноразові workflow з правом запису не додавати; публікацію релізу виконувати окремим кроком після зелених gates.
