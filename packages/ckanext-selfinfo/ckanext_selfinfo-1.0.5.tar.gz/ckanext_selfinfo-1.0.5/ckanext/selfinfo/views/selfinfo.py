from __future__ import annotations

import json
from typing import Any, cast
from flask import Blueprint
from flask.views import MethodView

from ckan import types
import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.lib.redis import connect_to_redis, Redis
from ckanext.selfinfo.utils import get_redis_key


selfinfo = Blueprint("selfinfo", __name__, url_prefix="/ckan-admin")


class SelfinfoView(MethodView):
    def get(self):
        try:
            context: types.Context = cast(types.Context, {
                "model": model,
                "user": tk.current_user.name,
                "auth_user_obj": tk.current_user
            })

            tk.check_access(u'sysadmin', context)
        except tk.NotAuthorized:
            tk.abort(404)
        
        args = tk.request.args

        if args.get('drop_errors') and tk.asbool(args['drop_errors']):
            redis: Redis = connect_to_redis()
            key = get_redis_key('errors')
            redis.set(key, json.dumps([]))

            return tk.redirect_to("selfinfo.index")

        data: dict[str, Any] = tk.get_action("get_selfinfo")({}, {})
        status_show: dict[str, Any] = tk.get_action("status_show")({}, {})

        return tk.render("selfinfo/index.html", {
            "data": data,
            "status_show": status_show,
            }
        )


selfinfo.add_url_rule(
    "/selfinfo",
    view_func=SelfinfoView.as_view("index"),
)
