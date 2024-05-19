"""Context editor."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import pynetbox

TContext = dict[str, Any]


LOG = logging.getLogger(__name__)


class NetboxUpdateError(Exception):
    """Exception for when updating a device failed."""


class NetboxObjectNotFoundError(Exception):
    """Exception for when no object was found."""


@dataclass
class NetboxObject:
    """Dataclass to hold a netbox object."""

    name: str
    id: int
    context: TContext = field(default_factory=dict)


class NetboxHandlerBase(ABC):
    """Abstract strategy base class for fetching the right kind of object."""

    def __init__(
        self, netbox_url: str, netbox_api_key: str, test_mode: bool = False
    ) -> None:
        """Initialize netbox context base class."""
        self.api = pynetbox.api(netbox_url, token=netbox_api_key)
        if not test_mode:
            api_status = self.api.status()
            assert isinstance(api_status["netbox-version"], str), (
                f"Could not read the Netbox API version from the server at {netbox_url}. "
                "The host or api token may be wrong."
            )

    @abstractmethod
    def get_one(
        self, *, name: str | None = None, id: int | None = None
    ) -> NetboxObject:
        """Get one element."""

    @abstractmethod
    def get_all(self) -> list[NetboxObject]:
        """Get all."""

    def as_dict(self) -> dict[str, TContext]:
        """Get all as dictionary."""
        return {vm.name: vm.context for vm in self.get_all()}

    @abstractmethod
    def update(
        self, context: TContext, *, name: str | None = None, id: int = None
    ) -> bool:
        """Update an object."""


class NetboxFileHandlerBase(ABC):
    """Strategy base class for handling files with contexts."""

    file_extension: str

    def __init__(self, directory: Path) -> None:
        """Initialize file handler strategy."""
        self.directory = directory
        assert (
            directory.exists() and directory.is_dir()
        ), "Directory does not exist or is not a directory."

    @abstractmethod
    def _from_object(self, context: TContext) -> str:
        """Render context.

        Must be implemented in the strategy implementation.
        """

    @abstractmethod
    def _to_object(self, text: str) -> dict[str, Any]:
        """Re-construct the context using the given strategy."""

    def write_to_dir(self, devices: dict[str, TContext]) -> None:
        """Write all contexts to the output directory."""
        for device, context in devices.items():
            self._write_context(device, context)

    def _write_context(self, devicename: str, context: dict[str, Any]) -> None:
        """Write file to directory."""
        filename = self.directory / f"{devicename}.{self.file_extension}"
        with open(filename, "w", encoding="utf-8") as f:
            LOG.debug(f"Writing context to {filename.absolute()}")
            f.write(self._from_object(context))

    def get_updated_from_dir(self, devices: dict[str, TContext]) -> dict[str, TContext]:
        """Read context from files."""
        changed: dict[Path, TContext] = {}
        for filename in self.directory.glob(f"*.{self.file_extension}"):
            with open(filename, "r", encoding="utf-8") as f:
                rendered = f.read()
                name = filename.stem
                previous_rendered = self._from_object(devices[name])
                if rendered != previous_rendered:
                    LOG.info(f"Found changes in context for {name}")
                    new_context = self._to_object(rendered)
                    changed[filename] = new_context
                else:
                    LOG.debug(f"Device {name} was not updated.")

        return changed
