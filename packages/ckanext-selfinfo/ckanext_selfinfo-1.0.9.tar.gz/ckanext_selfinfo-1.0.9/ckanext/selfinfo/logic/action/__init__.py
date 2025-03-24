from __future__ import annotations

from typing import Any

from . import get
from . import update


def get_actions():
    actions: dict[str, Any] = {
        "get_selfinfo": get.get_selfinfo,
        "update_last_module_check": update.update_last_module_check,
    }

    return actions
