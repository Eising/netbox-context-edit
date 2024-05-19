"""Test VMs.

Most of the mock stuff is blatantly stolen from pynetbox.
"""

from .util import NBContextMock
from netbox_context_edit.inventory import NetboxVM


class NetboxVMTest(NBContextMock.Tests):
    nb_context = "vm"
    nb_context_handler = NetboxVM
