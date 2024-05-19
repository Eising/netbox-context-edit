"""YAML strategy."""

from .main import NetboxFileHandlerBase, TContext

import yaml


class NetboxYamlContext(NetboxFileHandlerBase):
    """Manage netbox context as YAML."""

    file_extension = "yml"

    def _to_object(self, text: str) -> TContext:
        """Parse YAML into a context object."""
        return yaml.load(text, Loader=yaml.Loader)

    def _from_object(self, context: TContext) -> str:
        """Render context object as YAML."""
        return yaml.dump(context)
