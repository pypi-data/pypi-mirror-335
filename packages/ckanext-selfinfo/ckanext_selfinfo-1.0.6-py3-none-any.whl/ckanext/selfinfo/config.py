from __future__ import annotations

from typing import Literal

import ckan.plugins.toolkit as tk

SELFINFO_REDIS_PREFIX = 'ckan.selfinfo.redis_prefix_key'
SELFINFO_ERRORS_LIMIT = 'ckan.selfinfo.errors_limit'
SELFINFO_REPOS_PATH = 'ckan.selfinfo.ckan_repos_path'
SELFINFO_REPOS = 'ckan.selfinfo.ckan_repos'
SELFINFO_PARTITIONS_PATH = 'ckan.selfinfo.partitions'
SELFINFO_REDIS_SUFFIX: Literal["_selfinfo"] = "_selfinfo"
STORE_TIME: float = 604800.0 # one week
# STORE_TIME: float = 1.0
PYPI_URL: Literal["https://pypi.org/pypi/"] = "https://pypi.org/pypi/"


def selfinfo_get_redis_prefix():
    prefix = tk.config.get(SELFINFO_REDIS_PREFIX, '')
    return prefix + "_" if prefix else prefix


def selfinfo_get_errors_limit():
    return int(tk.config.get(SELFINFO_ERRORS_LIMIT, 20))


def selfinfo_get_repos_path():
    return tk.config.get(SELFINFO_REPOS_PATH)


def selfinfo_get_repos():
    return tk.config.get(SELFINFO_REPOS, '')

def selfinfo_get_partitions():
    return tk.config.get(SELFINFO_PARTITIONS_PATH, '/')
