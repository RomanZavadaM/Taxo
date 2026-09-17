# -*- coding: utf-8 -*-
"""Taxo application entry point from v8.70 candidate r11 onward."""
import main as core
from work_analysis_ext import install as install_work_analysis
from activity_register_60 import install as install_activity_register

App = install_activity_register(core, install_work_analysis(core))


def run():
    workspace_lock = core.prepare_workspace_interactively()
    if workspace_lock is None:
        return
    try:
        migrated, old_db = core.init_db()
        app = App()
        if migrated and old_db:
            app.after(300, lambda: core.messagebox.showinfo(
                "Дані перенесено автоматично",
                "Існуючу базу водіїв знайдено та один раз скопійовано у робоче сховище:\n\n"
                f"{core.DB_PATH}\n\nСтара база залишена без змін."
            ))
        app.mainloop()
    finally:
        workspace_lock.release()


if __name__ == "__main__":
    run()
