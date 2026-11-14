# PROJECT_STATE — Taxo

**Дата:** 14.11.2026.

## Поточний підтверджений стан

Taxo інтегрував і опублікував **10.19-r5**.

- Exact product / release source: `0ab0cc761078b38e391c1998ddf9feee7447d3a8`.
- Stable/Latest: **v10.18-r3**, без змін.
- Current Test prerelease: **v10.19-r5 — Test Portable**.
- 6 assets: Windows, Windows 7, macOS Intel, macOS ARM, START, SHA256.

## Реалізовано у r5

- user-facing path `Власні шаблони → Підготувати чернетку`;
- typed fact form для всіх типів r4;
- read-only registry adapter через `entity_choices`;
- stable-ID employee/driver/vehicle snapshots;
- multi-select participants;
- explicit driver–vehicle pair editor;
- pair invariant: один ТЗ → кілька водіїв допустимо; один водій → кілька різних ТЗ в одній чернетці блокується;
- exact source SHA guard проти stale form;
- усі Tk reads виконуються в UI thread;
- background rendering отримує лише plain Python facts;
- read-only preview без Save/Export/business side effects.

## Exact-source CI

Для `0ab0cc761078b38e391c1998ddf9feee7447d3a8`:
- START `43614552144` SUCCESS;
- Windows `43614552146` SUCCESS;
- Windows 7 `43614552095` SUCCESS;
- macOS Intel/ARM `43614552161` SUCCESS;
- Windows/Win7 Defender + post-scan integrity PASS.
- Publisher `43615561706` SUCCESS.
- Immutable release `v10.19-r5` target = exact product source.

## Merge/recovery note

r5 branch відставала від main на 5 службових recovery-комітів. Перетин файлів був нульовий: main змінював лише HANDOFF/PROJECT_STATE/WORKLOG/RELEASE_INDEX. Main підтягнуто звичайним merge commit без force; strict required `build-windows` після цього PASS.

## Наступна продуктова ревізія

**10.19-r6** — immutable snapshot заповненої чернетки як проміжний документний стан перед генерацією файлів.

r6 має:
- зберігати exact source template SHA/edit revision;
- зберігати normalized facts і rendered structured content;
- бути immutable після створення;
- мати workspace-relative storage/index та atomic write;
- входити в backup/restore;
- не створювати автоматично наказ/інструктаж;
- не генерувати DOCX/PDF;
- не створювати DocumentArchive, scan/signature state.

Після r6 окремими slices: DOCX renderer/export → PDF/print path → DocumentArchive.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
