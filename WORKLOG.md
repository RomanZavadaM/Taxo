# WORKLOG — Taxo

**Оновлено:** 29.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable.  
**Latest full multi-platform checkpoint:** Taxo **10.6-r10** / `v10.6-r10`.  
**Latest integrated code checkpoint in `main`:** **10.7-r6**.  
**Main merge:** `c47f145253660d6cfa008d6ca1030df9eaa7a353`.  
**Latest issued fast-test:** **10.7-r6** / `v10.7-r6` → exact source `fec6dc538db016d313bb6fc958a505e29e0faffc`.  
**Next code revision:** **10.7-r7**.  
**Knowledge branch:** `knowledge/vehicle-operations`.  
**Live ledger:** Issue #61.

## DONE — 10.7-r6

Тема: **backup перед 48-місячним retention**.

Підтверджений дефект E4: `init_db()` запускав `purge_old()` раніше за `auto_backup_database()`, тому записи, що саме цього запуску переходили за 48-місячну межу, могли бути видалені до створення автоматичної резервної копії.

Реалізовано:
- порядок змінено на `auto_backup_database()` → `purge_old()`;
- retention 48 місяців не змінено;
- склад очищуваних таблиць не змінено;
- E3 (`водій + зміна персоналу`) перевірено: загальний writer-баг подвійного плану не підтверджено; точні часові overlap-и вже блокуються;
- `v1076_features.py`, `tests/test_v10_7_r6.py`, release notes додані;
- історичний r5 identity-тест виправлено так, щоб він не заморожував поточну версію назавжди.

Verify / issuance:
- functional head `a9d739ebfc0f86b7e5f1e6cc0c862626d4630ea1`: Windows + macOS green;
- issued source `fec6dc538db016d313bb6fc958a505e29e0faffc`;
- publisher run `36611466842`: success, full regression green;
- issued-head Windows run `36611475819`: success;
- issued-head macOS run `36611475830`: success;
- immutable tag/prerelease: `v10.7-r6`;
- release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.7-r6
- START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.7-r6/Taxo_v10_7_candidate_r6_START.zip
- START SHA-256: `a96269f65923d90f6b515d6ad26f1134f560085ec632f4e1e38bf71cd617a127`;
- PR #95 retargeted to `main`, marked ready and merged;
- merge commit: `c47f145253660d6cfa008d6ca1030df9eaa7a353`.

Після issuance `v10.7-r6` не рухати і не перевидавати. Будь-яка наступна зміна коду = **10.7-r7**.

## DONE — 10.7-r5

- історичні кадрові звіти включають працівника за фактичним періодом працевлаштування, а не за поточним `active`;
- exact source `ed223e8af88216167b7db4d70413608d66bea9af`;
- immutable `v10.7-r5`.

## DONE — 10.7-r4

- накази, додатки та закріплення можна коригувати після внутрішнього затвердження;
- append-only історія змін;
- паперовий підпис не є технічним lock;
- exact source `a214eccc95a00d229f28e52865a5ec37b6f61bba`;
- immutable `v10.7-r4`.

## DONE — 10.7-r3

- структуровані додатки до наказів;
- PDF друкує додатки окремими сторінками;
- exact source `a51e336a31192fa7b82cb3bfe6db6c112dc70eae`;
- immutable `v10.7-r3`.

## DONE — 10.7-r2

- розділ `Експлуатація`;
- накази, закріплення ТЗ/водіїв, відповідальні особи;
- відомість ТЦК використовує підтверджені дані бази без службової provenance у формі для подання;
- exact source `346d21aacaf6c40563b6c9430f466f14dafd3543`;
- immutable `v10.7-r2`.

## DONE — 10.7-r1

- безпечне повторне розпізнавання тахографічних шайб;
- ручні інтервали не видаляються;
- виправлено wrap-around / cross-midnight;
- exact source `1a124bc8218aada5ab4b66f74376b02c7dc62481`;
- immutable `v10.7-r1`.

## PREVIOUS FULL CHECKPOINT — 10.6-r10

- exact source `0baad010d0c0d4f29db62f26c29d512c71058928`;
- Windows x64, Windows 7 SP1 x64, macOS ARM64, macOS Intel;
- immutable `v10.6-r10`;
- stable `v10.3` не пересувається.

## NEXT — 10.7-r7

1. Виправити PDF наказів: буквальні теги на кшталт `<b>№ 12</b>` не повинні друкуватися як текст.
2. Перевірити renderer наказів і додатків на HTML/XML-like артефакти, українські шрифти та перенос рядків.
3. Далі повернутися до підтверджених пунктів аудиту: межі тижня/режимів, activity register plan/fact, waybill.
4. ТО/ремонти будувати з `knowledge/vehicle-operations` та реальних документів користувача; нормативні твердження звіряти з чинними авторитетними джерелами.

## PRESERVED

- stable `v10.3` не пересувається без окремого рішення;
- issued tags `v10.7-r1` … `v10.7-r6` immutable;
- plan/fact не змішувати;
- паперовий підпис не блокує виправлення електронного запису, але історія змін зберігається;
- БД, персональні документи, скани та кеші не публікуються;
- кожний наступний кодовий крок змінює ревізію.

## BLOCKED

Немає.
