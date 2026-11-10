# HANDOFF_CURRENT — Taxo

**10.11.2026:** stable / Latest — [v10.15-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r4). Власник протестував перший каталог 10.15-r5 та повідомив, що зауважень не знайшов; рішення зробити r5 stable не надходило.

- [10.15-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r5) — опублікований prerelease, 8 файлів. Product/tag `0a5420cb9285ae5a8fc085c2689303d3e070ffbb`; каталог наказів і підготовлених документів інтегровано [PR #312](https://github.com/RomanZavadaM/Taxo/pull/312), без міграції старих даних і без завантаження сканів.
- Exact-product перевірки [START](https://github.com/RomanZavadaM/Taxo/actions/runs/42850673313), [Windows](https://github.com/RomanZavadaM/Taxo/actions/runs/42850673453), [Win7-сумісність](https://github.com/RomanZavadaM/Taxo/actions/runs/42850673934), [macOS Intel/ARM](https://github.com/RomanZavadaM/Taxo/actions/runs/42850673085) — SUCCESS; [publisher](https://github.com/RomanZavadaM/Taxo/actions/runs/42851842833) — SUCCESS. Фізичний Win7 та реальний SMB/NAS не перевірені.
- Старі великі частини ще не винесені: `main.py` — 16 644 рядки; розвантаження наказів та інструктажів залишається попереду. Опційні підписані копії не реалізовані.
- [Протокол r6: підписані копії та узгоджений резерв](https://github.com/RomanZavadaM/dev-strategy/blob/profile/taxo/taxo-history/SIGNED_COPIES_PROTOCOL_10_15_R6_2026-11-10.md) підготовлено на основі чинного коду. Це проєкт, не реалізація; визначені обмеження блокування, переривання, backup, restore і перенесення.
- [Приватний проєкт](https://github.com/RomanZavadaM/dev-strategy/blob/profile/taxo/taxo-history/DESIGN_DOCUMENTS_ORDERS_BRIEFINGS_2026-11-10.md) містить ризики й варіанти наступних кроків; [приватний журнал](https://github.com/RomanZavadaM/dev-strategy/blob/profile/taxo/taxo-history/DEVELOPMENT_LOG.md) — детальні докази. Копія попереднього exact-main START є в Drive, а нову резервну копію r5 тут ще не підтверджено.
- У виданому stable r4 START старий README; [актуальна документація](docs/releases/DOCUMENTATION_v10.15-r4.md) доступна окремо. Тег і файли r4 не змінювали.

## Наступна дія

Розпочати окрему ревізію **10.15-r6** за приватним протоколом: спочатку забезпечити і перевірити спільну синхронізацію запису документів, резервування і перенесення та життєвий цикл блокування сховища; потім реалізувати вкладення для одного типу документів. Виділення старих сценаріїв наказів та інструктажів — окремими перевірюваними кроками.

## Recovery

`START_HERE.md` → `HANDOFF_CURRENT.md` → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
