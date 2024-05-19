"""CLI script methods."""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, TypeGuard

import click

from .factory import virtual_machines
from .manager import NetboxContextManager


TNetboxContextFactory = Callable[[str, str, Path], NetboxContextManager]


def validate_context_factory(func: Any) -> TypeGuard[TNetboxContextFactory]:
    """Ensure that the netbox context manager factory is valid."""
    if func is not None and callable(func):
        return func
    raise RuntimeError("Invalid context type.")


def cli_context_to_netbox(ctx: click.Context, directory: Path) -> NetboxContextManager:
    """Extract Netbox context manager out of Click context."""
    netbox_context_mgr = validate_context_factory(ctx.obj.get("NETBOX_CONTEXT"))
    assert (
        netbox_context_mgr is not None
    ), "Could not find a valid netbox context manager."
    url, token = get_netbox(ctx)
    netbox_context: NetboxContextManager = netbox_context_mgr(url, token, directory)
    return netbox_context


def get_netbox(ctx: click.Context) -> tuple[str, str]:
    """Get netbox url and token."""
    arg_url = ctx.obj.get("URL")
    arg_token = ctx.obj.get("TOKEN")
    env_url = os.getenv("NETBOX_URL")
    env_token = os.getenv("NETBOX_API_TOKEN")
    if not any((arg_url, env_url)):
        raise click.UsageError(
            "No netbox URL found. Please either set it in your environment "
            "as NETBOX_URL, or pass it to the --url CLI option."
        )

    if not any((arg_token, env_token)):
        raise click.UsageError(
            "No netbox API token found. Please either set it in your environment "
            "as NETBOX_API_TOKEN, or pass it to the --token CLI option."
        )
    url = next(iter([elem for elem in (arg_url, env_url) if elem]))
    token = next(iter([elem for elem in (arg_token, env_token) if elem]))
    return (url, token)


formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
LOG = logging.getLogger(__name__)
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)


@click.group()
@click.option("--url", "-u", help="Netbox URL")
@click.option("--token", "-t", help="Netbox API token")
@click.option("--debug", is_flag=True, help="Enable debugging.")
@click.pass_context
def cli(ctx: click.Context, url: str, token: str, debug: bool) -> None:
    """Root CLI group."""
    if debug:
        LOG.setLevel(logging.DEBUG)

    ctx.ensure_object(dict)
    ctx.obj["URL"] = url
    ctx.obj["TOKEN"] = token


@cli.group()
@click.pass_context
def vm(ctx: click.Context) -> None:
    """Virtual Machines."""
    ctx.obj["OBJ_TYPE"] = "vm"
    ctx.obj["NETBOX_CONTEXT"] = virtual_machines
    ctx.obj["ITEM"] = "virtual machine"
    ctx.obj["ITEMS"] = "virtual machines"


@click.command()
@click.argument(
    "directory",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
)
@click.pass_context
def pull(ctx: click.Context, directory: Path) -> None:
    """Pull config into directory."""
    netbox_context = cli_context_to_netbox(ctx, directory)
    netbox_context.pull()
    item = ctx.obj.get("ITEM", "object")
    click.echo(
        f"Wrote {item} contexts to {click.style(directory.absolute(), bold=True)}."
    )


@click.command()
@click.argument(
    "directory",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
)
@click.pass_context
def push(ctx: click.Context, directory: Path) -> None:
    """Pull config into directory."""
    netbox_context = cli_context_to_netbox(ctx, directory)
    changed = netbox_context.push()
    items = ctx.obj.get("ITEMS", "objects")
    click.echo(f"{click.style(str(len(changed)), bold=True)} {items} pushed to netbox.")


@click.command()
@click.argument(
    "directory",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
)
@click.pass_context
def check(ctx: click.Context, directory: Path) -> None:
    """Check for changes in the local directory."""
    netbox_context = cli_context_to_netbox(ctx, directory)
    scriptname = Path(sys.argv[0]).name
    boldusage = click.style(
        f"{scriptname} push {ctx.obj['OBJ_TYPE']} {directory}", bold=True
    )
    changed = netbox_context.check()
    if len(changed) > 0:
        click.echo(f"Found {click.style(str(len(changed)), bold=True)} changed files:")
        for filename in changed:
            click.echo(f"  - {filename}")
        click.echo(f"Run {boldusage} to push your changes to netbox.")
    else:
        click.echo("No changes detected.")


vm.add_command(pull)
vm.add_command(push)
vm.add_command(check)


if __name__ == "__main__":
    cli()
