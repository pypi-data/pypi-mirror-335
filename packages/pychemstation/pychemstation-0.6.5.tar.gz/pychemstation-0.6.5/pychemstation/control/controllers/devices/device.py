import abc
from typing import Union

from ....control.controllers import CommunicationController
from ....control.controllers.tables.table import TableController
from ....utils.chromatogram import AgilentChannelChromatogramData
from ....utils.table_types import Table


class DeviceController(TableController, abc.ABC):

    def __init__(self, controller: CommunicationController, table: Table, offline: bool):
        super().__init__(controller, None, None, table, offline)

    @abc.abstractmethod
    def get_row(self, row: int):
        pass

    def retrieve_recent_data_files(self):
        raise NotImplementedError

    def get_data(self) -> Union[list[AgilentChannelChromatogramData], AgilentChannelChromatogramData]:
        raise NotImplementedError
