from ....control.controllers import CommunicationController
from .device import DeviceController
from ....utils.table_types import Table


class ColumnController(DeviceController):

    def __init__(self, controller: CommunicationController, table: Table):
        super().__init__(controller, table)

    def get_row(self, row: int):
        pass
