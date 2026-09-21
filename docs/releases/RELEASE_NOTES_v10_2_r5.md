# Taxo 10.2-r5 — cleanup історичного stable publisher

**Статус:** candidate / у перевірці  
**База:** Taxo 10.2-r4  
**Stable:** Taxo 10.1

## Причина

Після прийняття 10.2-r4 і злиття candidate у `main` GitHub автоматично запустив застарілий workflow `Publish Taxo 10.1 stable`.

Цей workflow був написаний для моменту публікації stable 10.1 і жорстко перевіряє `Version: 10.1`. Коли у `main` уже був `10.2-r4`, перевірка закономірно завершилась failure і GitHub надіслав червоне повідомлення, хоча сам 10.2-r4 був справний.

## Зміна

- `.github/workflows/publish-v10.1.yml` переведено у режим **workflow_dispatch only**.
- Автозапуск від push у `main` прибрано.
- Назву workflow змінено на `Historical publisher Taxo 10.1 stable (manual only)`.
- Stable release `v10.1` не пересувається й не переписується.
- Інші historical candidate publishers не зачіпаються: вони прив'язані до своїх старих work-гілок.

## Regression

Додано тест, який перевіряє, що historical 10.1 publisher:
- має `workflow_dispatch`;
- не містить `push:` у trigger-блоці;
- не слухає `main`.

Також чинні тести табеля, ролі водія, перепланування, пакетування та правила ревізій залишаються в regression gate.

## Пакет

Тестовий пакет цього кроку: `Taxo_v10_2_candidate_r5_START.zip`.

Наступний завершений кодовий крок після r5 — `10.2-r6`.
