"""Context editor."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import pynetbox


from loguru import logger

logger.disable("main")


class NetboxVMContextBase(ABC):
    """Abstract base class for managingt Netbox VM contexts."""

    file_extension: str

    def __init__(self, directory: Path, netbox_url: str, netbox_api_key: str) -> None:
        """Initialize netbox context base class."""
        self.api = pynetbox.api(netbox_url, token=netbox_api_key)
        self.path = directory
        self._devices: dict[str, dict[str, Any]] | None = None

    @property
    def devices(self) -> dict[str, dict[str, Any]]:
        """Get devices."""
        if self._devices:
            return self._devices
        devices = self.api.virtualization.virtual_machines.all()
        self._devices = {device.name: device.local_context_data for device in devices}
        return self._devices

    @abstractmethod
    def _render_context(self, context: dict[str, Any]) -> str:
        """Render context.

        Must be implemented in the strategy implementation.
        """

    @abstractmethod
    def _parse_rendered(self, text: str) -> dict[str, Any]:
        """Re-construct the context using the given strategy."""

    def write_to_dir(self) -> None:
        """Write all contexts to the output directory."""
        for device, context in self.devices.items():
            self._write_context(device, context)

    def _write_context(self, devicename: str, context: dict[str, Any]) -> None:
        """Write file to directory."""
        filename = self.path / f"{devicename}.{self.file_extension}"
        with open(filename, "w", encoding="utf-8") as f:
            logger.debug(f"Writing context to {filename.absolute()}")
            f.write(self._render_context(context))

    def _update_device(self, name: str, new_context: dict[str, Any]) -> None:
        """Update device."""
        device = self.api.virtualization.virtual_machines.get(name=name)
        if not device:
            raise RuntimeError(f"Could not find a device called {name}")
        device.local_context_data = new_context
        result = device.save()
        if not result:
            raise RuntimeError(
                f"Update towards netbox failed for device {name}, new context: {new_context!r}"
            )

    @abstractmethod
    def _get_updated_device_context(
        self, name: str, rendered_context: str
    ) -> dict[str, Any] | None:
        """Check if the context needs to be updated.

        Return updated context dictionary if update is necessary.
        """

    def update_from_dir(self, dry_run: bool = False) -> None:
        """Read context from files."""
        changed: list[Path] = []
        for filename in self.path.glob(f"*.{self.file_extension}"):
            with open(filename, "r", encoding="utf-8") as f:
                rendered = f.read()
                name = filename.stem
                new_context = self._get_updated_device_context(name, rendered)
                if new_context:
                    logger.info(f"Found changes in context for {name}")
                    changed.append(filename)
                    if not dry_run:
                        logger.info(
                            f"Updating context of {name} from file {filename.absolute()}"
                        )
                        self._update_device(name, new_context)
                else:
                    logger.debug(f"Device {name} was not updated.")
