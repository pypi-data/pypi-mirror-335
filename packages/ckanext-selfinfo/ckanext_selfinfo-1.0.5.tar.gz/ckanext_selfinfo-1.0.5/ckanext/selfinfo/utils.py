from __future__ import annotations

import os
from typing import Any, Mapping
import requests
import psutil
from psutil._common import bytes2human
import platform
import git
from datetime import datetime
import importlib_metadata as imetadata
import logging
import json

from ckan.lib.redis import connect_to_redis, Redis
import ckan.plugins.toolkit as tk
from .config import (
    selfinfo_get_redis_prefix,
    selfinfo_get_repos_path,
    selfinfo_get_partitions,
    SELFINFO_REDIS_SUFFIX,
    STORE_TIME,
    PYPI_URL,
)

log = logging.getLogger(__name__)


def get_redis_key(name):
    return selfinfo_get_redis_prefix() + name + SELFINFO_REDIS_SUFFIX


def get_python_modules_info(force_reset: bool=False) -> dict[str, Any]:
    redis: Redis = connect_to_redis()    
    now: float = datetime.utcnow().timestamp()
    
    groups: dict[str, Any] = {"ckan": {}, "ckanext": {}, "other": {}}
    pdistribs: Mapping[str, Any] = imetadata.packages_distributions()
    modules: dict[str, Any] = {
        p.name: p.version for p in imetadata.distributions()}

    for i, p in pdistribs.items():
            for module in p:
                group: str = i if i in groups else "other"

                if module in module and not module in groups[group]:
                    redis_key: str = get_redis_key(module)
                    data: Mapping[str, Any] = {
                        "name": module,
                        "current_version": modules.get(module, 'unknown'),
                        "updated": now,
                    }
                    if not redis.hgetall(redis_key):
                        data["latest_version"] = get_lib_latest_version(module)
                        redis.hset(redis_key, mapping=data)

                    if (now - float(redis.hget(redis_key, "updated").decode("utf-8"))) > STORE_TIME or force_reset:
                        data["latest_version"] = get_lib_latest_version(module)
                        for key in data:
                            if data[key] != redis.hget(redis_key, key):
                                redis.hset(redis_key, key=key, value=data[key])

                    groups[group][module] = {k.decode("utf-8"): v.decode("utf-8") for k, v in redis.hgetall(redis_key).items()}
    
                    groups[group][module]["updated"] = datetime.fromtimestamp(float(groups[group][module]["updated"]))

    groups["ckanext"] = dict(sorted(groups["ckanext"].items()))
    groups["other"] = dict(sorted(groups["other"].items()))

    return groups


def get_freeze():
    try:
        from pip._internal.operations import freeze
    except ImportError: # pip < 10.0
        from pip.operations import freeze
    pkgs = freeze.freeze()
    pkgs = list(pkgs)
    pkgs_string = "\n".join(list(pkgs))
    return {
        "modules": pkgs,
        "modules_html": f"""{pkgs_string}""",
    }


def get_lib_data(lib):
    req = requests.get(PYPI_URL + lib + '/json', headers={
        "Content-Type": "application/json"
    })

    if req.status_code == 200:
        return req.json()
    return None


def get_lib_latest_version(lib):
    data = get_lib_data(lib)
    
    if data and data.get('info'):
        return data['info'].get('version', 'unknown')
    return 'unknown'


def get_ram_usage() -> dict[str, Any]:
    memory = psutil.virtual_memory()
    return {
        "precent_usage": memory[2],
        "used_ram": bytes2human(memory[3], format="%(value).1f")
    }


def get_disk_usage():
    paths = selfinfo_get_partitions()
    results = []
    for path in paths.split(','):
        try:
            usage = psutil.disk_usage(path.strip())
            if usage:
                results.append(
                    {
                        "path": path,
                        "precent_usage":  usage.percent,
                        "total_disk": bytes2human(usage.total, format="%(value).1f%(symbol)s"),
                        "free_space": bytes2human(usage.free, format="%(value).1f%(symbol)s")
                    }
                )
        except OSError:
            log.exception(f"Path '{path}' does not exists.")
    return results


def get_platform_info() -> dict[str, Any]:
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }


def gather_git_info():
    ckan_repos_path = selfinfo_get_repos_path()
    repos_info: list[dict[str,Any]] = []
    if ckan_repos_path:
        ckan_repos = tk.config.get('ckan.selfinfo.ckan_repos', '')
        list_repos = ckan_repos.strip().split(" ") if \
            ckan_repos else [
                name for name in os.listdir(
                    ckan_repos_path) if os.path.isdir(
                        os.path.join(ckan_repos_path, name)) and not name.startswith('.')
        ]
        repos: dict[str, git.Repo] = {
            repo: get_git_repo(ckan_repos_path + '/' + repo) for repo in list_repos if repo}

        for name, repo in repos.items():

            commit, branch = repo.head.object.name_rev.strip().split(" ")
            short_sha: str = repo.git.rev_parse(commit, short=True)
            on = 'branch'

            if repo.head.is_detached and branch.startswith("remotes/"):
                branch = short_sha
                on = 'commit'
            elif repo.head.is_detached and branch.startswith("tags/"):
                on = 'tag'
            elif repo.head.is_detached and (
                not branch.startswith("tags/") and not branch.startswith("remotes/")):
                branch = short_sha
                on = 'commit'

            repos_info.append({
                "name": name,
                "head": branch,
                "commit": short_sha,
                "on": on,
                "remotes": [
                    {
                        "name": remote.name,
                        "url": remote.url,
                        } for remote in repo.remotes
                    ]
            })

    return repos_info


def get_git_repo(path):
    repo = git.Repo(path)
    return repo


def retrieve_errors():
    redis: Redis = connect_to_redis()
    key = get_redis_key('errors')
    if not redis.exists(key):
        redis.set(key, json.dumps([]))
    return json.loads(redis.get(key))
