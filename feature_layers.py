# -*- coding: utf-8 -*-
"""Ordered Taxo runtime feature-layer registry.

The project historically accumulated versioned ``install()`` wrappers directly
inside ``taxo_app.py``. Keeping the order in one registry makes future modules
additive: a new feature is one descriptor instead of another nested expression
or another entry-point rewrite.

Issued legacy layers keep their original installer signatures. New layers can
opt in to the explicit r8 application-services context, allowing future code to
avoid importing the historical ``main`` namespace just to reach infrastructure.

This module intentionally preserves the existing import and install order.
It does not change business rules, database schema or user data.
"""
from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Tuple

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
from waybill_integrity import install as install_waybill_integrity
from vehicle_document_validity import install as install_vehicle_document_validity

Installer = Callable[..., type]


@dataclass(frozen=True)
class FeatureLayer:
    """One ordered, immutable runtime extension descriptor."""

    feature_id: str
    installer: Installer
    bootstrap: bool = False
    domain: str = "core"
    uses_services: bool = False


FEATURE_LAYERS: Tuple[FeatureLayer, ...] = (
    FeatureLayer("work-analysis-r10", install_work_analysis, bootstrap=True, domain="worktime"),
    FeatureLayer("activity-register-60", install_activity_register, domain="worktime"),
    FeatureLayer("v9-release", install_v9),
    FeatureLayer("hotfix-901", install_hotfix_901),
    FeatureLayer("v91-features", install_v91),
    FeatureLayer("personnel-v91", install_personnel, domain="personnel"),
    FeatureLayer("v1043", install_v1043),
    FeatureLayer("v1044", install_v1044),
    FeatureLayer("v1045", install_v1045),
    FeatureLayer("v1046", install_v1046),
    FeatureLayer("v1048", install_v1048),
    FeatureLayer("v1049", install_v1049),
    FeatureLayer("military-accounting-ui", install_military_accounting_ui, domain="military-accounting"),
    FeatureLayer("v10410", install_v10410),
    FeatureLayer("v1051", install_v1051),
    FeatureLayer("v1052", install_v1052),
    FeatureLayer("v1053", install_v1053),
    FeatureLayer("v1054", install_v1054),
    FeatureLayer("v1055", install_v1055),
    FeatureLayer("v1056", install_v1056),
    FeatureLayer("v1057", install_v1057),
    FeatureLayer("v1058", install_v1058),
    FeatureLayer("v1059", install_v1059),
    FeatureLayer("v10510", install_v10510),
    FeatureLayer("v1061", install_v1061),
    FeatureLayer("v1062", install_v1062),
    FeatureLayer("v1063", install_v1063),
    FeatureLayer("v1064", install_v1064),
    FeatureLayer("v1065", install_v1065),
    FeatureLayer("v1066", install_v1066),
    FeatureLayer("v1067", install_v1067),
    FeatureLayer("v1068", install_v1068),
    FeatureLayer("v1069", install_v1069),
    FeatureLayer("v10610", install_v10610),
    FeatureLayer("v1071", install_v1071),
    FeatureLayer("v1072", install_v1072),
    FeatureLayer("v1073", install_v1073),
    FeatureLayer("v1074", install_v1074),
    FeatureLayer("v1074-appendix-history", install_v1074_appendix_history),
    FeatureLayer("v1075", install_v1075),
    FeatureLayer("v1076", install_v1076),
    FeatureLayer("v1077", install_v1077),
    FeatureLayer("v1078", install_v1078),
    FeatureLayer("v1079", install_v1079),
    FeatureLayer("v10710", install_v10710),
    FeatureLayer("v1081", install_v1081),
    FeatureLayer("v1082", install_v1082),
    FeatureLayer("v1083", install_v1083),
    FeatureLayer("v1084-stoir", install_v1084, domain="maintenance"),
    FeatureLayer("v1085-stoir", install_v1085, domain="maintenance"),
    FeatureLayer("v1092-waybill-integrity", install_waybill_integrity, domain="waybills"),
    FeatureLayer("v1093-vehicle-document-validity", install_vehicle_document_validity, domain="vehicles"),
)


def validate_feature_layers(layers: Sequence[FeatureLayer] = FEATURE_LAYERS) -> None:
    """Fail early when extension metadata is ambiguous or structurally unsafe."""

    if not layers:
        raise RuntimeError("Taxo feature registry is empty")
    ids = [layer.feature_id for layer in layers]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Taxo feature registry contains duplicate feature_id values")
    bootstrap_positions = [index for index, layer in enumerate(layers) if layer.bootstrap]
    if bootstrap_positions != [0]:
        raise RuntimeError("Exactly the first Taxo feature layer must be bootstrap")
    for layer in layers:
        if not callable(layer.installer):
            raise RuntimeError(f"Installer for {layer.feature_id} is not callable")


def feature_layer_ids(layers: Sequence[FeatureLayer] = FEATURE_LAYERS) -> Tuple[str, ...]:
    return tuple(layer.feature_id for layer in layers)


def install_feature_layers(core, layers: Sequence[FeatureLayer] = FEATURE_LAYERS, services=None):
    """Build the current App class by applying every registered layer in order.

    Legacy layers keep the historical signatures ``install(core)`` and
    ``install(core, App)``. A future layer may set ``uses_services=True`` and
    receive the explicit application services as the final argument.
    """

    validate_feature_layers(layers)
    app_cls: Optional[type] = None
    for layer in layers:
        if layer.uses_services and services is None:
            raise RuntimeError(f"Feature {layer.feature_id} requires application services")
        if layer.bootstrap:
            app_cls = layer.installer(core, services) if layer.uses_services else layer.installer(core)
        else:
            if app_cls is None:
                raise RuntimeError(f"Feature {layer.feature_id} has no base App class")
            app_cls = (
                layer.installer(core, app_cls, services)
                if layer.uses_services
                else layer.installer(core, app_cls)
            )
        if app_cls is None:
            raise RuntimeError(f"Feature {layer.feature_id} returned no App class")
    if app_cls is not None and services is not None:
        # New code can access infrastructure through self.services without
        # importing main. Existing feature classes remain untouched.
        app_cls.services = services
    return app_cls
