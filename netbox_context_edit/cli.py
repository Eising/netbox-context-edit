"""CLI script methods."""

import logging
import click

from .factory import subcommand


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


# Register subcommands for models we support.

cli.add_command(subcommand("vm"))

# cli.group(subcommand("vm"))

if __name__ == "__main__":
    cli()
