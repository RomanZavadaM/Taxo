# AUDIT — Taxo 10.1-r3 approved UI shell

**Дата:** 20.09.2026  
**Stable baseline:** Taxo 10.0 / `v10.0`  
**Previous candidate:** `v10.1-r2`  
**Work branch:** `work/v10.1-driver-role-ui-refresh`

## Причина r3

Ручне порівняння показало, що 10.1-r2 не відтворював затверджений макет: було змінено палітру, branding і окремі форми, але збережено старий верхній menu row та видимий Notebook tab strip. Загальний табель також лишався окремим старим Toplevel.

## Виправлення

1. Головне вікно переведено на явний shell `header + sidebar + content + status bar`.
2. Native Tk menu на Windows/Linux прихований та перенесений у overflow `☰`; macOS зберігає штатний глобальний menu.
3. Видимий Notebook tab strip прибраний через `Shell.TNotebook`; сторінки переключаються sidebar-ом.
4. Затверджений logo artwork вбудовано як text-free PNG і використовується для header/runtime/build icon; програмне наближене перемальовування більше не є джерелом логотипа.
5. Sidebar має власні monochrome vector icons, active state і дорожній footer motif.
6. Верхня шапка має dynamic enterprise name, слоган, локальний час, user block і Settings.
7. Sidebar «Працівники» перенаправлено на `tab_personnel`; legacy driver-card page більше не є основною сторінкою персоналу.
8. Реєстр персоналу працює всередині main shell і має пошук, лічильник та основні кадрові дії.
9. Загальний табель отримав такий самий shell із sidebar і operational footer.
10. Жодна з цих змін не змінює схему БД або розрахункову модель робочого часу.

## Regression focus

`tests/test_v10_1_r3.py` перевіряє:
- r3 version marker;
- прихований native tab row та використання sidebar shell;
- header clock / workstation / footer enterprise;
- перенесення Windows/Linux menu у header overflow;
- той самий sidebar shell у загальному табелі;
- відсутність фіксованого «АТП Завада» у brand artwork.

## Release policy

`v10.1-r3` може бути тільки prerelease/source checkpoint після green regression gate. `main` не зливається до ручної Windows-перевірки затвердженого дизайну.
