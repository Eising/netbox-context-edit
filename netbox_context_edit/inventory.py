"""Inventory strategies."""

from .main import (
    NetboxHandlerBase,
    NetboxObject,
    NetboxObjectNotFoundError,
    NetboxUpdateError,
    TContext,
)


class NetboxVM(NetboxHandlerBase):
    """Strategy for working with Virtual Machines."""

    def get_one(
        self, *, name: str | None = None, id: int | None = None
    ) -> NetboxObject:
        """Get a single virtual machine."""
        if not name and not id:
            raise ValueError("No name or id provided.")

        if id:
            result = self.api.virtualization.virtual_machines.get(id=id)
            if not result:
                raise NetboxObjectNotFoundError(
                    f"Could not fetch a virtual machine with id {id}"
                )
        else:
            result = self.api.virtualization.virtual_machines.get(name=name)
            if not result:
                raise NetboxObjectNotFoundError(
                    f"Could not fetch a virtual machine with name {name}"
                )

        assert result is not None
        return NetboxObject(
            name=result.name, id=result.id, context=result.local_context_data
        )

    def get_all(self) -> list[NetboxObject]:
        """Get all virtual machines."""
        all_vms = self.api.virtualization.virtual_machines.all()
        return [
            NetboxObject(name=vm.name, id=vm.id, context=vm.local_context_data)
            for vm in all_vms
        ]

    def update(
        self, context: TContext, *, name: str | None = None, id: int | None = None
    ) -> None:
        """Update VM context."""
        if not name and not id:
            raise ValueError("No name or id provided.")
        if id:
            vm = self.api.virtualization.virtual_machines.get(id=id)
            if not vm:
                raise NetboxObjectNotFoundError(
                    f"Could not fetch a virtual machine with id {id}"
                )
        else:
            vm = self.api.virtualization.virtual_machines.get(name=name)
            if not vm:
                raise NetboxObjectNotFoundError(
                    f"Could not fetch a virtual machine with name {name}"
                )

        vm.local_context_data = context
        result = vm.save()
        if not result:
            raise NetboxUpdateError(
                f"Could not update the context on VM {vm.name} with id {vm.id}. "
                "Ensure that the context is valid, and that the API key has "
                "permissions to update the VM."
            )
