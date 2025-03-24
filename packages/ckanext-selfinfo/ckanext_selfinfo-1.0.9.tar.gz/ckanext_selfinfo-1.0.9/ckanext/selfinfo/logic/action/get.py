from __future__ import annotations

from typing import Any


from ckan import types
import ckan.plugins.toolkit as tk
import ckan.plugins as p

import ckanext.selfinfo.utils as selfutils
from ckanext.selfinfo.interfaces import ISelfinfo


@tk.side_effect_free
def get_selfinfo(
    context: types.Context,
    data_dict: dict[str, Any],
) -> dict[str, Any]:
    
    tk.check_access("sysadmin", context, data_dict)
    
    platform_info: dict[str, Any] = selfutils.get_platform_info()
    ram_usage: dict[str, Any] = selfutils.get_ram_usage()
    disk_usage: list[dict[str, Any]] = selfutils.get_disk_usage()
    groups: dict[str, Any] = selfutils.get_python_modules_info(
        force_reset=data_dict.get("force-reset", False),
    )
    freeze = selfutils.get_freeze()
    git_info = selfutils.gather_git_info()
    errors = selfutils.retrieve_errors()
    actions = selfutils.ckan_actions()
    auth = selfutils.ckan_auth_actions()
    blueprints = selfutils.ckan_bluprints()
    helpers = selfutils.ckan_helpers()

    data = {
        "groups": groups,
        "platform_info": platform_info,
        "ram_usage": ram_usage,
        "disk_usage": disk_usage,
        "git_info": git_info,
        "freeze": freeze,
        "errors": errors,
        "actions": actions,
        "auth": auth,
        "blueprints": blueprints,
        "helpers": helpers,
    }

    # data modification
    for item in p.PluginImplementations(ISelfinfo):
        item.selfinfo_after_prepared(data)

    return data
