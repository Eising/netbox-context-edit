"""Factory functions."""

from functools import partial
from pathlib import Path

import click

from .main import NetboxHandlerBase, NetboxFileHandlerBase
from .context_yaml import NetboxYamlContext
from .inventory import NetboxVM
from .manager import NetboxContextManager
from . import cli_commands


# def virtual_machines(
#     netbox_url: str, netbox_api_key: str, directory: Path
# ) -> NetboxContextManager:
#     """Create a manager for virtual machines outputting YAML."""
#     return NetboxContextManager(
#         netbox_url,
#         netbox_api_key,
#         directory,
#         NetboxVM(netbox_url, netbox_api_key),
#         NetboxYamlContext(directory),
#     )


FILE_HANDLER = NetboxYamlContext
MODELS: dict[str, tuple[str, NetboxHandlerBase]] = {
    "vm": ("Virtual machines", NetboxVM)
}


def create_manager(
    nb_handler: NetboxHandlerBase,
    file_handler: NetboxFileHandlerBase,
    netbox_url: str,
    netbox_api_key: str,
    directory: Path,
) -> NetboxContextManager:
    """Create a netbox context manager."""
    return NetboxContextManager(
        netbox_url,
        netbox_api_key,
        directory,
        nb_handler,
        file_handler,
    )


def subcommand(model_name: str) -> click.Group:
    """Create a subcommand for a model."""
    description, nb_handler = MODELS[model_name]

    @click.group(
        model_name,
        commands=[cli_commands.pull, cli_commands.push, cli_commands.check],
        help=description,
    )
    @click.pass_context
    def callback(ctx: click.Context):
        """Create group callback."""
        ctx.obj["OBJ_TYPE"] = model_name
        ctx.obj["NETBOX_CONTEXT"] = partial(create_manager, nb_handler, FILE_HANDLER)
        ctx.obj["ITEM"] = model_name
        ctx.obj["ITEMS"] = f"{model_name}s"

    return callback
