"""CLI script methods."""

import os
import sys
from pathlib import Path
from functools import wraps

import click

from .context_yaml import NetboxYamlContex

from loguru import logger


def get_netbox() -> tuple[str, str]:
    """Get netbox url and token."""
    url = os.getenv("NETBOX_URL")
    token = os.getenv("NETBOX_API_TOKEN")

    if not all((url, token)):
        raise RuntimeError(
            "Missing environment variables. Please set NETBOX_URL and NETBOX_API_TOKEN."
        )

    assert url is not None
    assert token is not None

    return (url, token)


@click.group()
def cli():
    """Manage the local configuration context of virtual machines in Netbox from your file system.

    Netbox authentication can be provided either with the --url and --token
    argments, or using the environment variables NETBOX_URL and NETBOX_API_TOKEN.
    """

    pass


def common_parameters(func):
    """Common parameters decorator."""

    @click.argument(
        "destination",
        type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
    )
    @click.option("--url", "-u", help="Netbox URL")
    @click.option("--token", "-t", help="Netbox API token")
    @click.option("--debug", is_flag=True, help="Enable debugging.")
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@cli.command()
@common_parameters
def pull(
    destination: Path,
    url: str | None = None,
    token: str | None = None,
    debug: bool = False,
) -> None:
    """Pull context data from netbox into a directory."""
    if not url:
        url, _ = get_netbox()
    if not token:
        token, _ = get_netbox()
    context = NetboxYamlContex(destination, url, token, debug)
    context.write_to_dir()


@cli.command()
@common_parameters
def check(
    destination: Path,
    url: str | None = None,
    token: str | None = None,
    debug: bool = False,
) -> None:
    """Check if any files are updated."""
    if not url:
        url, _ = get_netbox()
    if not token:
        _, token = get_netbox()
    context = NetboxYamlContex(destination, url, token, debug)
    changed = context.update_from_dir(dry_run=True)
    if changed:
        click.echo("Files with updates:")
        for filepath in changed:
            click.echo(f"  - {filepath}")
        click.echo()
        scriptname = Path(sys.argv[0]).name
        boldusage = click.style(f"{scriptname} push {destination}", bold=True)
        click.echo(f"Run {boldusage} to push the changes to netbox.")
    else:
        click.echo("No changes detected!")


@cli.command()
@common_parameters
def push(
    destination: Path,
    url: str | None = None,
    token: str | None = None,
    debug: bool = False,
) -> None:
    """Write changes back to netbox."""
    if not url:
        url, _ = get_netbox()
    if not token:
        token, _ = get_netbox()
    context = NetboxYamlContex(destination, url, token, debug)
    context.update_from_dir(dry_run=False)


if __name__ == "__main__":
    cli()
