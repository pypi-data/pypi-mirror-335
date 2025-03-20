from __future__ import annotations

from typing import Any


from ckan import types
import ckan.plugins.toolkit as tk
import ckanext.selfinfo.utils as selfutils


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

    return {
        "groups": groups,
        "platform_info": platform_info,
        "ram_usage": ram_usage,
        "disk_usage": disk_usage,
        "git_info": git_info,
        "freeze": freeze,
        "errors": errors,
    }
