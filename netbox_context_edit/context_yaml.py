"""YAML strategy."""

from typing import Any
from .main import NetboxVMContextBase

import yaml


class NetboxYamlContex(NetboxVMContextBase):
    """Manage netbox context as YAML."""

    file_extension = "yml"

    def _parse_rendered(self, text: str) -> dict[str, Any]:
        """Parse YAML into a context object."""
        return yaml.load(text, Loader=yaml.Loader)

    def _render_context(self, context: dict[str, Any]) -> str:
        """Render context object as YAML."""
        return yaml.dump(context)

    def _get_updated_device_context(
        self, name: str, rendered_context: str
    ) -> dict[str, Any] | None:
        """Get an updated context, if it has changed."""
        context = self.devices[name]
        old_rendered_context = self._render_context(context)
        if old_rendered_context != rendered_context:
            return self._parse_rendered(rendered_context)
        return None
