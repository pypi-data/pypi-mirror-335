from __future__ import annotations

from typing import Any
import pytest
import platform
import os

from ckan import model
import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_action
import ckan.tests.factories as factories

current_path: list[str] = os.getcwd().split("/")
current_path.pop()
updated_path: str = "/".join(current_path)


@pytest.mark.ckan_config("ckan.plugins", "selfinfo")
@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.selfinfo.ckan_repos_path", updated_path)
@pytest.mark.ckan_config("ckan.selfinfo.ckan_repos", "ckan ckanext-selfinfo")
class TestGET:
    def test_get_selfinfo(self):
        user = factories.User()
        sysadmin = factories.Sysadmin()
        context: dict[str, Any] = {
            "model": model,
            "user": user["name"],
            "ignore_auth": False,
        }

        with pytest.raises(tk.NotAuthorized):
            call_action("get_selfinfo", context=context)

        context["user"] = sysadmin['name']
        
        selfinfo: dict[str, Any] = tk.get_action("get_selfinfo")(context, {})

        assert type(selfinfo) == dict
        
        assert len(selfinfo.keys()) == 4
        
        assert selfinfo["platform_info"]["python_version"] == platform.python_version()
