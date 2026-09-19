# -*- coding: utf-8 -*-
"""Taxo 10.0 stable application entry point."""
import main as core
from work_analysis_ext import install as install_work_analysis
from activity_register_60 import install as install_activity_register
from v9_release import install as install_v9
from hotfix_901 import install as install_hotfix_901
from v91_features import install as install_v91
from personnel_v91 import install as install_personnel

App = install_personnel(
    core,
    install_v91(
        core,
        install_hotfix_901(
            core,
            install_v9(
                core,
                install_activity_register(core, install_work_analysis(core)),
            ),
        ),
    ),
)


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
