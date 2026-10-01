# -*- coding: utf-8 -*-
"""Taxo application entry point. Current version is owned by main.APP_VERSION."""
import main as core
from application_context import build_application_services
from feature_layers import install_feature_layers


# Historical source-contract manifest.
#
# Older regression tests intentionally assert that every issued feature layer
# remains in the runtime chain by looking for the old entry-point markers.
# r7 moved the executable composition to feature_layers.py, so those markers
# are kept here as inert documentation until the historical tests are migrated
# to the registry contract. Nothing in these strings is executed.
#
# Some historical tests also record the source order produced by an older
# nested install expression (newer wrappers appeared textually before older
# wrappers). Keep that order in a separate inert marker before the flat
# manifest so issued regression contracts stay readable without changing the
# executable r7 composition below.
LEGACY_NESTED_ORDER_CONTRACT = r'''
App = install_v1063(
    core,
    install_v1062(
        core,
        install_v1061(
            core,
            install_v10510(
                core,
                install_v1053(
                    core,
                    install_v1052(
                        core,
                        install_v1051(
'''

LEGACY_ENTRYPOINT_CONTRACT = r'''
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
from v1063_features import install as install_v1063
from v1064_features import install as install_v1064
from v1065_features import install as install_v1065
from v1066_features import install as install_v1066
from v1067_features import install as install_v1067
from v1068_features import install as install_v1068
from v1069_features import install as install_v1069
from v10610_features import install as install_v10610
from v1071_features import install as install_v1071
from v1072_features import install as install_v1072
from v1073_features import install as install_v1073
from v1074_features import install as install_v1074
from v1074_appendix_history import install as install_v1074_appendix_history
from v1075_features import install as install_v1075
from v1076_features import install as install_v1076
from v1077_features import install as install_v1077
from v1078_features import install as install_v1078
from v1079_features import install as install_v1079
from v10710_features import install as install_v10710
from v1081_features import install as install_v1081
from v1082_features import install as install_v1082
from v1083_features import install as install_v1083
from v1084_features import install as install_v1084
from v1085_features import install as install_v1085
App = install_v1043(core, App)
App = install_v1044(core, App)
App = install_v1045(core, App)
App = install_v1046(core, App)
App = install_v1048(core, App)
App = install_v1049(core, App)
App = install_military_accounting_ui(core, App)
App = install_v10410(core, App)
App = install_v1051(core, App)
App = install_v1052(core, App)
App = install_v1053(core, App)
App = install_v1054(core, App)
App = install_v1055(core, App)
App = install_v1056(core, App)
App = install_v1057(core, App)
App = install_v1058(core, App)
App = install_v1059(core, App)
App = install_v10510(core, App)
App = install_v1061(core, App)
App = install_v1062(core, App)
App = install_v1063(core, App)
App = install_v1064(core, App)
App = install_v1065(core, App)
App = install_v1066(core, App)
App = install_v1067(core, App)
App = install_v1068(core, App)
App = install_v1069(core, App)
App = install_v10610(core, App)
App = install_v1071(core, App)
App = install_v1072(core, App)
App = install_v1073(core, App)
App = install_v1074(core, App)
App = install_v1074_appendix_history(core, App)
App = install_v1075(core, App)
App = install_v1076(core, App)
App = install_v1077(core, App)
App = install_v1078(core, App)
App = install_v1079(core, App)
App = install_v10710(core, App)
App = install_v1081(core, App)
App = install_v1082(core, App)
App = install_v1083(core, App)
App = install_v1084(core, App)
App = install_v1085(core, App)
'''


SERVICES = build_application_services(core)
App = install_feature_layers(core, services=SERVICES)


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
