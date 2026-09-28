# -*- coding: utf-8 -*-
"""Taxo application entry point. Current version is owned by main.APP_VERSION."""
import main as core
from work_analysis_ext import install as install_work_analysis
from activity_register_60 import install as install_activity_register
from v9_release import install as install_v9
from hotfix_901 import install as install_hotfix_901
from v91_features import install as install_v91
from personnel_v91 import install as install_personnel
from v1043_features import install as install_v1043
from v1044_features import install as install_v1044
from v1045_features import install as install_v1045
from v1046_features import install as install_v1046
from v1048_features import install as install_v1048
from v1049_features import install as install_v1049
from military_accounting_ui import install as install_military_accounting_ui
from v10410_features import install as install_v10410
from v1051_features import install as install_v1051
from v1052_features import install as install_v1052
from v1053_features import install as install_v1053
from v1054_features import install as install_v1054
from v1055_features import install as install_v1055
from v1056_features import install as install_v1056
from v1057_features import install as install_v1057
from v1058_features import install as install_v1058
from v1059_features import install as install_v1059
from v10510_features import install as install_v10510
from v1061_features import install as install_v1061
from v1062_features import install as install_v1062

App = install_v1062(
    core,
    install_v1061(
        core,
        install_v10510(
            core,
            install_v1059(
                core,
                install_v1058(
                    core,
                    install_v1057(
                        core,
                        install_v1056(
                            core,
                            install_v1055(
                                core,
                                install_v1054(
                                    core,
                                    install_v1053(
                                        core,
                                        install_v1052(
                                            core,
                                            install_v1051(
                                                core,
                                                install_v10410(
                                                    core,
                                                    install_military_accounting_ui(
                                                        core,
                                                        install_v1049(
                                                            core,
                                                            install_v1048(
                                                                core,
                                                                install_v1046(
                                                                    core,
                                                                    install_v1045(
                                                                        core,
                                                                        install_v1044(
                                                                            core,
                                                                            install_v1043(
                                                                                core,
                                                                                install_personnel(
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
                                                                                ),
                                                                            ),
                                                                        ),
                                                                    ),
                                                                ),
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
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
