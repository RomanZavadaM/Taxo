# -*- coding: utf-8 -*-
"""Taxo 10.7-r9 — practical operations-order templates.

The templates are editable starting text, not legal conclusions. They intentionally
avoid hard-coding article/paragraph numbers that can become obsolete.
"""
from __future__ import annotations

APP_VERSION = "10.7-r9"

TYPE_RESPONSIBLE_PERSONS = "responsible_persons"
TYPE_VEHICLE_RELEASE_RETURN = "vehicle_release_return"
TYPE_SEASONAL_OPERATION = "seasonal_operation"

DEFAULT_BODY_TEMPLATES = {
    "vehicle_storage": (
        "1. Визначити місця зберігання транспортних засобів підприємства відповідно до фактичної організації роботи.\n"
        "2. Відповідальним особам забезпечити облік місць зберігання та змін до них.\n"
        "3. Водіям дотримуватися встановленого порядку постановки транспортних засобів на зберігання."
    ),
    "summarized_worktime": (
        "1. Організувати облік робочого часу працівників за затвердженими графіками з окремим відображенням плану і факту.\n"
        "2. Відповідальним особам забезпечити своєчасне внесення фактичних відхилень і підтвердних документів.\n"
        "3. Під час формування табеля використовувати фактичні дані; заміна відсутнього факту планом допускається лише після явного підтвердження користувача."
    ),
    "driver_rest_places": (
        "1. Визначити місця відпочинку водіїв, які використовуються під час виконання рейсів і маршрутів.\n"
        "2. Вести актуальний перелік таких місць та умов їх використання.\n"
        "3. Зміни місць відпочинку оформлювати окремою зміною до цього наказу або новим наказом."
    ),
    "driver_training": (
        "1. Організувати спеціальну підготовку та стажування водіїв відповідно до затвердженої на підприємстві програми.\n"
        "2. Визначити наставників, строки та транспортні засоби для стажування у додатку або окремому переліку.\n"
        "3. Результати підготовки та стажування оформлювати документально."
    ),
    "safety_training": (
        "1. Організувати навчання, інструктажі та перевірку знань працівників за напрямами, що стосуються їхніх обов'язків.\n"
        "2. Визначити відповідальних осіб, строки та перелік працівників у додатку до наказу.\n"
        "3. Результати навчання і перевірки знань фіксувати у відповідних журналах або протоколах."
    ),
    "road_safety": (
        "1. Організувати системну роботу з безпеки дорожнього руху на підприємстві.\n"
        "2. Визначити відповідальних за аналіз подій, профілактичні заходи та доведення вимог до водіїв.\n"
        "3. Заходи та результати їх виконання фіксувати у відповідних документах підприємства."
    ),
    "technical_control": (
        "1. Організувати контроль технічного стану транспортних засобів перед допуском до експлуатації.\n"
        "2. Визначити відповідальних осіб і порядок документування результатів контролю.\n"
        "3. Транспортні засоби з виявленими несправностями не допускати до експлуатації до усунення причин."
    ),
    "maintenance_repair": (
        "1. Організувати планування технічного обслуговування, ремонту та оглядів транспортних засобів.\n"
        "2. Вести облік виконаних робіт, дат, пробігу та відповідальних виконавців.\n"
        "3. Відхилення від плану та позапланові ремонти фіксувати окремими записами без видалення історії."
    ),
    "accident_commission": (
        "1. Створити комісію для документування обставин події та збору наявних матеріалів.\n"
        "2. Комісії зафіксувати фактичні обставини, пояснення, документи та інші матеріали без попереднього визначення вини.\n"
        "3. За результатами роботи оформити висновок та перелік запропонованих заходів."
    ),
    "occupational_safety": (
        "1. Організувати роботу з охорони праці відповідно до фактичних видів робіт підприємства.\n"
        "2. Визначити відповідальних осіб за інструктажі, навчання, облік та контроль виконання заходів.\n"
        "3. Підтвердні записи і документи зберігати у відповідних журналах та реєстрах."
    ),
    "fire_safety": (
        "1. Організувати виконання протипожежних заходів у приміщеннях, на території та у транспортних засобах підприємства.\n"
        "2. Визначити відповідальних осіб і порядок контролю наявності та стану засобів пожежної безпеки.\n"
        "3. Проведені інструктажі, перевірки та виявлені недоліки документувати."
    ),
    TYPE_RESPONSIBLE_PERSONS: (
        "1. Призначити відповідальних осіб за напрями експлуатаційної роботи згідно з переліком у додатку до наказу.\n"
        "2. Відповідальним особам забезпечити ведення документів і своєчасне повідомлення про зміни, що впливають на їхній напрям роботи.\n"
        "3. У разі зміни відповідальної особи оформлювати новий наказ або зміну до чинного наказу."
    ),
    TYPE_VEHICLE_RELEASE_RETURN: (
        "1. Встановити внутрішній порядок підготовки, випуску транспортних засобів на лінію та їх приймання після повернення.\n"
        "2. Визначити відповідальних осіб і послідовність фактичних відміток про допуск, виїзд, повернення та виявлені несправності.\n"
        "3. Дані шляхового листа та інших первинних документів вносити за фактом виконаних дій."
    ),
    TYPE_SEASONAL_OPERATION: (
        "1. Провести сезонну підготовку транспортних засобів до умов майбутнього періоду експлуатації.\n"
        "2. Перелік транспортних засобів, робіт, строків та відповідальних осіб визначити у додатку до наказу.\n"
        "3. Виконані роботи й виявлені недоліки зафіксувати у документах технічного обліку."
    ),
}


def install(core, base_app):
    if getattr(core, "_TAXO_V1079_INSTALLED", False):
        return base_app

    import operations_orders as ops

    ops.TYPE_RESPONSIBLE_PERSONS = TYPE_RESPONSIBLE_PERSONS
    ops.TYPE_VEHICLE_RELEASE_RETURN = TYPE_VEHICLE_RELEASE_RETURN
    ops.TYPE_SEASONAL_OPERATION = TYPE_SEASONAL_OPERATION

    ops.ORDER_TYPE_LABELS.update({
        TYPE_RESPONSIBLE_PERSONS: "Призначення відповідальних осіб",
        TYPE_VEHICLE_RELEASE_RETURN: "Порядок випуску ТЗ на лінію та повернення",
        TYPE_SEASONAL_OPERATION: "Сезонна підготовка транспортних засобів",
    })
    ops.ORDER_TYPE_GROUP.update({
        TYPE_RESPONSIBLE_PERSONS: ops.ORDER_GROUP_OTHER,
        TYPE_VEHICLE_RELEASE_RETURN: ops.ORDER_GROUP_VEHICLES,
        TYPE_SEASONAL_OPERATION: ops.ORDER_GROUP_VEHICLES,
    })
    ops.ORDER_GROUP_TYPES = {
        group: tuple(order_type for order_type in ops.ORDER_TYPE_LABELS
                     if ops.ORDER_TYPE_GROUP.get(order_type) == group)
        for group in ops.ORDER_GROUP_LABELS
    }
    ops.DEFAULT_SUBJECTS.update({
        TYPE_RESPONSIBLE_PERSONS: "Про призначення відповідальних осіб за напрямами експлуатаційної роботи",
        TYPE_VEHICLE_RELEASE_RETURN: "Про порядок випуску транспортних засобів на лінію та їх повернення",
        TYPE_SEASONAL_OPERATION: "Про сезонну підготовку транспортних засобів",
    })
    ops.DEFAULT_PREAMBLES.update({
        TYPE_RESPONSIBLE_PERSONS: "З метою визначення персональної відповідальності за основні напрями експлуатаційної роботи —",
        TYPE_VEHICLE_RELEASE_RETURN: "З метою впорядкування фактичного допуску, випуску та повернення транспортних засобів —",
        TYPE_SEASONAL_OPERATION: "З метою підготовки транспортних засобів до сезонних умов експлуатації —",
    })
    ops.DEFAULT_BODY_TEMPLATES = dict(DEFAULT_BODY_TEMPLATES)

    original_create_order = ops.create_order
    if not getattr(original_create_order, "_taxo_v1079_wrapped", False):
        def create_order_with_template(con, *, order_type, order_no, order_date, place="", subject="",
                                       preamble="", body_text="", control_employee_id=None, note=""):
            if not str(body_text or "").strip():
                body_text = ops.DEFAULT_BODY_TEMPLATES.get(order_type, "")
            return original_create_order(
                con, order_type=order_type, order_no=order_no, order_date=order_date,
                place=place, subject=subject, preamble=preamble, body_text=body_text,
                control_employee_id=control_employee_id, note=note,
            )
        create_order_with_template._taxo_v1079_wrapped = True
        ops.create_order = create_order_with_template

    core.APP_VERSION = APP_VERSION
    core._TAXO_V1079_INSTALLED = True
    return base_app
