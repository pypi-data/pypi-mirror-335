from __future__ import annotations

from typing import Any
import click
from prettytable import PrettyTable

import ckan.plugins.toolkit as tk


@click.argument("module", required=True)
def update_module_info(module: str):    
    tk.get_action("update_last_module_check")({
        "ignore_auth": True},
        {"module": module,
        }
    )


def get_selfinfo():
    data = tk.get_action("get_selfinfo")({
        "ignore_auth": True},
        {}
    )

    platform_info: dict[str, Any] = data.get('platform_info', {})
    ram_usage: dict[str, Any] = data.get('ram_usage', {})
    platform_table = PrettyTable(["System", "Python Version", "RAM Usage %", "RAM Usage GB"])
    
    platform_table.add_row([
        platform_info.get("platform"),
        platform_info.get("python_version"),
        ram_usage.get("precent_usage"),
        ram_usage.get("used_ram"),
        ]
    )
    click.echo(click.style("System Information", fg='green'))
    
    click.echo(platform_table)
    groups_order: list[dict[str, Any]] = [
        {"name": "ckan", "label": "CKAN"},
        {"name": "ckanext", "label": "CKANEXT"},
        {"name": "other", "label": "Other"},
    ]
    groups:dict[str, Any] = data.get('groups', {})
    
    for item in groups_order:
        click.echo(click.style(item["label"], fg='green'))
        item_table = PrettyTable(["Name", "Current Version", "Possible Version", "Last Checked"])

        for key, values in groups.get(item["name"], {}).items():
            name = values.get('name')
            if name:
                item_table.add_row([
                    name,
                    values.get("current_version"),
                    values.get("latest_version"),
                    values.get("updated"),
                ], divider=True)
        
        click.echo(item_table)
