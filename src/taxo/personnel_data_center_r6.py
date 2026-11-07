# -*- coding: utf-8 -*-
"""Taxo 10.10-r6 — unified personnel data / registry / Diia center.

This layer does not replace historical registry storage. It provides one human
entry point over the existing import, working-data, Diia, military-accounting
and employee-document features, and adds safe bulk application from the latest
immutable registry snapshot.
"""
from __future__ import annotations

from datetime import datetime

import employee_document_register as docreg
import personnel_registry as registry
import personnel_registry_lossless as lossless
import registry_working_data as working

from v1045_features import _selected_employee_id
from v1048_features import _configure_window

APP_VERSION = "10.10-r6"

MODE_FILL_EMPTY = "fill_empty"
MODE_ACCEPT_NONCRITICAL = "accept_noncritical"

CRITICAL_FIELDS = {
    ("personal", "rnokpp"),
    ("personal", "birth_date"),
    ("personal", "passport_series"),
    ("personal", "passport_number"),
    ("personal", "id_card_number"),
    ("military", "registry_person_id"),
}


def _text(value):
    return str(value or "").strip()


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def _walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from _walk(child)


def _employee_name(row):
    return " ".join(
        _text(row[key])
        for key in ("last_name", "first_name", "middle_name")
        if _text(row[key])
    )


def _latest_snapshot_values(con, employee_id):
    rows = lossless.latest_raw_snapshot(con, int(employee_id))
    personal = {}
    military = {}
    source_name = ""
    imported_at = ""
    source_kind = ""
    for row in rows:
        if not source_name:
            source_name = _text(row["source_name"])
            imported_at = _text(row["imported_at"])
            source_kind = _text(row["source_kind"])
        scope = _text(row["canonical_scope"])
        field = _text(row["canonical_field"])
        value = _text(row["canonical_value"])
        if not field or not value:
            continue
        if scope == "personal" and field in working.PERSONAL_FIELDS:
            personal[field] = value
        elif scope == "military" and field in working.MILITARY_FIELDS:
            military[field] = value
    return {
        "source_name": source_name,
        "source_kind": source_kind,
        "imported_at": imported_at,
        "personal": personal,
        "military": military,
    }


def _comparison_for_employee(con, employee_id):
    current = working.employee_working_data(con, int(employee_id))
    latest = _latest_snapshot_values(con, int(employee_id))
    fill = []
    differences = []
    critical = []
    same = 0
    for scope, incoming in (("personal", latest["personal"]), ("military", latest["military"])):
        local_values = current[scope]
        for field, value in incoming.items():
            local = _text(local_values.get(field, ""))
            if not local:
                fill.append((scope, field, value))
            elif local == value:
                same += 1
            else:
                differences.append((scope, field, local, value))
                if (scope, field) in CRITICAL_FIELDS:
                    critical.append((scope, field, local, value))
    return {
        "current": current,
        "latest": latest,
        "fill": fill,
        "differences": differences,
        "critical": critical,
        "same": same,
    }


def registry_bulk_preview(con, active_only=True):
    working.ensure_personnel_schema(con)
    sql = "SELECT * FROM employees"
    if active_only:
        sql += " WHERE COALESCE(active,1)=1"
    sql += " ORDER BY last_name,first_name,middle_name,id"
    result = []
    for employee in con.execute(sql).fetchall():
        comp = _comparison_for_employee(con, employee["id"])
        latest = comp["latest"]
        if not latest["personal"] and not latest["military"]:
            continue
        result.append({
            "employee_id": int(employee["id"]),
            "employee_name": _employee_name(employee) or ("ID %s" % employee["id"]),
            "personnel_no": _text(employee["personnel_no"]) if "personnel_no" in employee.keys() else "",
            "source_name": latest["source_name"],
            "source_kind": latest["source_kind"],
            "imported_at": latest["imported_at"],
            "fill_count": len(comp["fill"]),
            "difference_count": len(comp["differences"]),
            "critical_count": len(comp["critical"]),
            "same_count": comp["same"],
        })
    return result


def apply_registry_bulk(con, employee_ids, mode):
    if mode not in (MODE_FILL_EMPTY, MODE_ACCEPT_NONCRITICAL):
        raise ValueError("Невідомий режим масового застосування.")
    changed_employees = 0
    changed_fields = 0
    skipped_critical = 0
    for employee_id in [int(x) for x in employee_ids]:
        comp = _comparison_for_employee(con, employee_id)
        personal = {}
        military = {}

        for scope, field, value in comp["fill"]:
            target = personal if scope == "personal" else military
            target[field] = value

        if mode == MODE_ACCEPT_NONCRITICAL:
            for scope, field, _local, value in comp["differences"]:
                if (scope, field) in CRITICAL_FIELDS:
                    skipped_critical += 1
                    continue
                target = personal if scope == "personal" else military
                target[field] = value
        else:
            skipped_critical += len(comp["critical"])

        if personal or military:
            working.save_employee_working_data(
                con,
                employee_id,
                personal_values=personal,
                military_values=military,
            )
            changed_employees += 1
            changed_fields += len(personal) + len(military)

    return {
        "changed_employees": changed_employees,
        "changed_fields": changed_fields,
        "skipped_critical": skipped_critical,
    }


def _latest_imports(con):
    registry.ensure_schema_on_connection(con)
    rows = con.execute(
        """SELECT * FROM employee_registry_imports
            ORDER BY imported_at DESC,id DESC"""
    ).fetchall()
    found = {}
    for row in rows:
        kind = _text(row["source_kind"])
        if kind not in found:
            found[kind] = row
    return found


def install(core, base_app):
    if getattr(core, "_TAXO_1010_R6_PERSONNEL_DATA_CENTER", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1010R6App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_personnel_data_center_r6()

        def _install_personnel_data_center_r6(self):
            root = getattr(self, "personnel_overview_page", None)
            if not _alive(root) or getattr(self, "_personnel_data_center_r6_installed", False):
                return

            # Current Personnel UI exposes the Data Center as a permanent action.
            # Historical compositions may still need the compatibility fallback.
            route_button = None
            anchor = None
            for widget in _walk(root):
                try:
                    if widget.winfo_class() not in ("TButton", "Button"):
                        continue
                    label = _text(widget.cget("text"))
                except Exception:
                    continue
                if label == "Дані / Дія / документи…":
                    route_button = widget
                    break
                if label == "Новий працівник":
                    anchor = widget

            if route_button is None:
                if anchor is None:
                    # Fail safe: never hide historical entry points unless the
                    # replacement route can actually be installed.
                    return
                try:
                    route_button = core.ttk.Button(
                        anchor.master,
                        text="Дані / Дія / документи…",
                        style="Accent.TButton",
                        command=self.open_personnel_data_center_r6,
                    )
                    route_button.pack(side="right", padx=(8, 0))
                except Exception:
                    try:
                        route_button.destroy()
                    except Exception:
                        pass
                    return

            self._personnel_data_center_r6_button = route_button
            self._personnel_data_center_r6_installed = True

            # Only after a replacement route is guaranteed do we remove the
            # historical clutter from the primary employee toolbar.
            for widget in list(_walk(root)):
                try:
                    if widget.winfo_class() not in ("TButton", "Button"):
                        continue
                    label = _text(widget.cget("text"))
                except Exception:
                    continue
                if (
                    label.startswith("Реєстр працівників:")
                    or label in {
                        "Імпорт з реєстру…",
                        "Дані та документи…",
                        "Реєстр документів",
                        "Військові дані / Дія",
                        "Військовий облік 2026",
                        "Звіряння через Дію",
                    }
                ):
                    try:
                        manager = str(widget.winfo_manager() or "")
                    except Exception:
                        manager = ""
                    forget = {
                        "pack": "pack_forget",
                        "grid": "grid_remove",
                        "place": "place_forget",
                    }.get(manager)
                    if forget:
                        try:
                            getattr(widget, forget)()
                        except Exception:
                            pass

        def open_personnel_data_center_r6(self):
            existing = getattr(self, "_personnel_data_center_r6_window", None)
            if _alive(existing):
                existing.lift()
                return

            win = core.tk.Toplevel(self)
            self._personnel_data_center_r6_window = win
            _configure_window(core, win, "Працівники — дані, Дія та документи", 1120, 760)
            body = core.ttk.Frame(win, padding=14)
            body.pack(fill="both", expand=True)

            core.ttk.Label(
                body,
                text="Працівники — дані, Дія та документи",
                style="Title.TLabel",
            ).pack(anchor="w")
            core.ttk.Label(
                body,
                text=(
                    "Єдина точка входу для двох державних XLSX, масового поновлення робочих даних, "
                    "офіційного циклу Дії та документів працівників. Оригінальні імпортовані знімки "
                    "не переписуються."
                ),
                style="Muted.TLabel",
                wraplength=1060,
                justify="left",
            ).pack(anchor="w", pady=(4, 10))

            import_status = core.tk.StringVar(value="")
            selected_status = core.tk.StringVar(value="")

            registry_box = core.ttk.LabelFrame(body, text="1. Дані з державних відомостей", padding=10)
            registry_box.pack(fill="x", pady=(0, 10))
            core.ttk.Label(
                registry_box,
                text=(
                    "Taxo підтримує обидва формати: «Відомості персонального обліку» і "
                    "«Відомості про працівників». Тип файла визначається автоматично."
                ),
                wraplength=1020,
                justify="left",
            ).pack(anchor="w")
            core.ttk.Label(
                registry_box,
                textvariable=import_status,
                style="Muted.TLabel",
                justify="left",
                wraplength=1020,
            ).pack(anchor="w", pady=(5, 8))
            rb = core.ttk.Frame(registry_box)
            rb.pack(fill="x")
            core.ttk.Button(
                rb,
                text="Завантажити XLSX / звірити…",
                style="Accent.TButton",
                command=self.import_personnel_registry_xlsx,
            ).pack(side="left")
            core.ttk.Button(
                rb,
                text="Масові дії з останнього імпорту…",
                command=self.open_personnel_registry_bulk_actions_r6,
            ).pack(side="left", padx=6)

            selected_box = core.ttk.LabelFrame(body, text="2. Вибраний працівник", padding=10)
            selected_box.pack(fill="x", pady=(0, 10))
            core.ttk.Label(selected_box, textvariable=selected_status, style="Subtitle.TLabel").pack(anchor="w")
            sb = core.ttk.Frame(selected_box)
            sb.pack(fill="x", pady=(8, 0))
            core.ttk.Button(
                sb,
                text="Робочі дані з реєстрів",
                command=self.open_employee_military_working_data,
            ).pack(side="left")
            core.ttk.Button(
                sb,
                text="Картка та документи",
                command=self.open_personnel_data_center,
            ).pack(side="left", padx=6)

            documents_box = core.ttk.LabelFrame(body, text="3. Документи працівників", padding=10)
            documents_box.pack(fill="x", pady=(0, 10))
            core.ttk.Label(
                documents_box,
                text=(
                    "Загальний реєстр усіх документів із фільтрами за строком, типом і джерелом. "
                    "Обов'язковість і контроль строку задаються для конкретного працівника; локальні файли "
                    "документів зберігаються у робочому сховищі Taxo."
                ),
                wraplength=1020,
                justify="left",
            ).pack(anchor="w")
            db = core.ttk.Frame(documents_box)
            db.pack(fill="x", pady=(8, 0))
            core.ttk.Button(
                db,
                text="Відкрити реєстр документів",
                command=self.open_employee_document_register,
            ).pack(side="left")
            if hasattr(self, "open_required_employee_documents_r7"):
                core.ttk.Button(
                    db,
                    text="Контроль обов'язкових документів…",
                    command=self.open_required_employee_documents_r7,
                ).pack(side="left", padx=6)

            official_box = core.ttk.LabelFrame(body, text="4. Офіційне звіряння та військовий облік", padding=10)
            official_box.pack(fill="x", pady=(0, 10))
            core.ttk.Label(
                official_box,
                text=(
                    "Імпорт XLSX і офіційна фіксація в Дії — різні речі. Тут залишені окремо "
                    "офіційний цикл Дії та контроль військового обліку."
                ),
                wraplength=1020,
                justify="left",
            ).pack(anchor="w")
            ob = core.ttk.Frame(official_box)
            ob.pack(fill="x", pady=(8, 0))
            core.ttk.Button(
                ob,
                text="Офіційний цикл Дії…",
                command=self.open_diia_reconciliation_cycle,
            ).pack(side="left")
            core.ttk.Button(
                ob,
                text="Військовий облік / строки…",
                command=self.open_military_accounting_overview,
            ).pack(side="left", padx=6)

            footer = core.ttk.Frame(body)
            footer.pack(fill="x", pady=(4, 0))

            def refresh():
                con = core.db()
                try:
                    latest = _latest_imports(con)
                    selected_id = _selected_employee_id(self)
                    selected_row = (
                        con.execute("SELECT * FROM employees WHERE id=?", (selected_id,)).fetchone()
                        if selected_id is not None else None
                    )
                finally:
                    con.close()

                labels = []
                for kind, title in (
                    (registry.SOURCE_DETAILED, "Відомості персонального обліку"),
                    (registry.SOURCE_SUMMARY, "Відомості про працівників"),
                ):
                    row = latest.get(kind)
                    if row is None:
                        labels.append("%s: ще не завантажено" % title)
                    else:
                        stamp = _text(row["imported_at"]).replace("T", " ")[:16]
                        labels.append("%s: %s · %s" % (title, _text(row["source_name"]) or "файл", stamp or "дата невідома"))
                import_status.set("\n".join(labels))
                selected_status.set(
                    "Вибрано: %s" % (_employee_name(selected_row) if selected_row is not None else "працівника не вибрано")
                )

            core.ttk.Button(footer, text="Оновити", command=refresh).pack(side="left")
            core.ttk.Button(footer, text="Закрити", command=win.destroy).pack(side="right")
            refresh()
            win.transient(self)

        def open_personnel_registry_bulk_actions_r6(self):
            existing = getattr(self, "_personnel_registry_bulk_r6_window", None)
            if _alive(existing):
                existing.lift()
                return

            win = core.tk.Toplevel(self)
            self._personnel_registry_bulk_r6_window = win
            _configure_window(core, win, "Масове поновлення даних працівників", 1120, 720)
            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)

            core.ttk.Label(body, text="Масове поновлення з останніх державних відомостей", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=(
                    "Виберіть одного або кількох працівників. Безпечний режим заповнює лише порожні поля. "
                    "Режим поновлення також приймає непорожні зміни, але ключові ідентифікаційні реквізити "
                    "(РНОКПП, дата народження, паспорт/ID та ідентифікатор у Реєстрі) ніколи не переписуються масово."
                ),
                style="Muted.TLabel",
                wraplength=1060,
                justify="left",
            ).pack(anchor="w", pady=(4, 10))

            table = core.ttk.Frame(body)
            table.pack(fill="both", expand=True)
            table.rowconfigure(0, weight=1)
            table.columnconfigure(0, weight=1)
            cols = ("employee", "source", "imported", "fill", "diff", "critical")
            tree = core.ttk.Treeview(table, columns=cols, show="headings", selectmode="extended")
            for key, label, width in (
                ("employee", "Працівник", 270),
                ("source", "Останній файл", 250),
                ("imported", "Імпорт", 135),
                ("fill", "Порожніх", 85),
                ("diff", "Відмінностей", 100),
                ("critical", "Критичних", 90),
            ):
                tree.heading(key, text=label)
                tree.column(key, width=width, anchor="w")
            sy = core.ttk.Scrollbar(table, orient="vertical", command=tree.yview)
            sx = core.ttk.Scrollbar(table, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
            tree.grid(row=0, column=0, sticky="nsew")
            sy.grid(row=0, column=1, sticky="ns")
            sx.grid(row=1, column=0, sticky="ew")
            tree.tag_configure("critical", foreground="#8A1C1C")
            tree.tag_configure("difference", foreground="#7A5B00")
            cache = {}

            summary_var = core.tk.StringVar(value="")
            core.ttk.Label(body, textvariable=summary_var, style="Muted.TLabel").pack(anchor="w", pady=(6, 0))

            def refresh():
                for iid in tree.get_children(""):
                    tree.delete(iid)
                cache.clear()
                con = core.db()
                try:
                    rows = registry_bulk_preview(con, active_only=True)
                finally:
                    con.close()
                total_fill = total_diff = total_critical = 0
                for row in rows:
                    iid = str(row["employee_id"])
                    cache[int(row["employee_id"])] = row
                    total_fill += row["fill_count"]
                    total_diff += row["difference_count"]
                    total_critical += row["critical_count"]
                    tag = "critical" if row["critical_count"] else ("difference" if row["difference_count"] else "")
                    tree.insert(
                        "", "end", iid=iid,
                        values=(
                            row["employee_name"],
                            row["source_name"] or "—",
                            row["imported_at"].replace("T", " ")[:16] or "—",
                            row["fill_count"],
                            row["difference_count"],
                            row["critical_count"],
                        ),
                        tags=((tag,) if tag else ()),
                    )
                summary_var.set(
                    "Працівників з імпортом: %d · порожніх полів: %d · відмінностей: %d · критичних: %d"
                    % (len(rows), total_fill, total_diff, total_critical)
                )

            def selected_ids():
                ids = []
                for iid in tree.selection():
                    try:
                        ids.append(int(iid))
                    except ValueError:
                        pass
                if not ids:
                    core.messagebox.showinfo("Масове поновлення", "Виберіть працівників у таблиці.", parent=win)
                return ids

            def select_all():
                tree.selection_set(tree.get_children(""))

            def apply(mode):
                ids = selected_ids()
                if not ids:
                    return
                selected_rows = [cache[x] for x in ids if x in cache]
                fill_count = sum(x["fill_count"] for x in selected_rows)
                diff_count = sum(x["difference_count"] for x in selected_rows)
                critical_count = sum(x["critical_count"] for x in selected_rows)
                if mode == MODE_FILL_EMPTY:
                    message = (
                        "Для %d працівників буде заповнено до %d порожніх полів. "
                        "Наявні значення не змінюються. Продовжити?"
                    ) % (len(ids), fill_count)
                else:
                    message = (
                        "Для %d працівників буде заповнено до %d порожніх полів і прийнято до %d "
                        "неідентифікаційних відмінностей. %d критичних ідентифікаційних значень "
                        "залишаться для ручної перевірки. Продовжити?"
                    ) % (len(ids), fill_count, max(0, diff_count - critical_count), critical_count)
                if not core.messagebox.askyesno("Масове поновлення", message, parent=win):
                    return

                # Mass changes receive a database safety checkpoint first.
                try:
                    backup_fn = getattr(core, "backup_database", None)
                    if callable(backup_fn):
                        backup_fn("before_personnel_registry_bulk")
                except Exception as exc:
                    if not core.messagebox.askyesno(
                        "Резервна копія",
                        "Не вдалося створити резервну копію перед масовою зміною:\n%s\n\nПродовжити без неї?" % exc,
                        parent=win,
                    ):
                        return

                con = core.db()
                try:
                    result = apply_registry_bulk(con, ids, mode)
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Масове поновлення", str(exc), parent=win)
                    return
                finally:
                    con.close()

                refresh_overview = getattr(self, "_refresh_personnel_overview", None)
                if callable(refresh_overview):
                    refresh_overview()
                refresh()
                core.messagebox.showinfo(
                    "Масове поновлення",
                    "Змінено працівників: %d\nЗмінено полів: %d\nКритичних полів залишено для ручної перевірки: %d"
                    % (
                        result["changed_employees"],
                        result["changed_fields"],
                        result["skipped_critical"],
                    ),
                    parent=win,
                )

            actions = core.ttk.Frame(body)
            actions.pack(fill="x", pady=(10, 0))
            core.ttk.Button(actions, text="Вибрати всіх", command=select_all).pack(side="left")
            core.ttk.Button(
                actions,
                text="Заповнити порожні у вибраних",
                style="Accent.TButton",
                command=lambda: apply(MODE_FILL_EMPTY),
            ).pack(side="left", padx=6)
            core.ttk.Button(
                actions,
                text="Прийняти реєстрові зміни у вибраних",
                command=lambda: apply(MODE_ACCEPT_NONCRITICAL),
            ).pack(side="left", padx=6)
            core.ttk.Button(actions, text="Оновити", command=refresh).pack(side="left", padx=6)
            core.ttk.Button(actions, text="Закрити", command=win.destroy).pack(side="right")

            refresh()
            win.transient(self)

    Taxo1010R6App.__name__ = "App"
    Taxo1010R6App.__qualname__ = "App"
    core.App = Taxo1010R6App
    core._TAXO_1010_R6_PERSONNEL_DATA_CENTER = True
    return Taxo1010R6App
