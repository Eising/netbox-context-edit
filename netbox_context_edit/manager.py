"""Manager class."""

from pathlib import Path
from typing import Type
from .main import NetboxFileHandlerBase, NetboxHandlerBase, TContext


class NetboxContextManager:
    """Netbox context manager class."""

    def __init__(
        self,
        netbox_url: str,
        netbox_api_key: str,
        directory: Path,
        netbox_object: Type[NetboxHandlerBase],
        file_handler: Type[NetboxFileHandlerBase],
    ) -> None:
        """Initialize context manager."""
        self.object_context = netbox_object(netbox_url, netbox_api_key)
        self.file_handler = file_handler(directory)

    def pull(self) -> dict[str, TContext]:
        """Get all contexts."""
        self.file_handler.write_to_dir(self.object_context.as_dict())

    def check(self) -> list[Path]:
        """Check which files have been updated."""
        return self.file_handler.update_from_dir(
            self.object_context.as_dict(), dry_run=True
        )

    def push(self) -> list[Path]:
        """Push updated contexts back to netbox."""
        return self.file_handler.update_from_dir(
            self.object_context.as_dict(), dry_run=False
        )
