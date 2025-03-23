import click

from . import main

def get_commands():
    return [selfinfo]


@click.group()
def selfinfo():
    """ckanext-selfinfo management commands."""
    
selfinfo.command(main.update_module_info)
selfinfo.command(main.get_selfinfo)
