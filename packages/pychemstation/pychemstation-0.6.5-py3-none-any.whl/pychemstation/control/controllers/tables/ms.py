from typing import Union

from ....control.controllers import CommunicationController
from ....control.controllers.tables.table import TableController
from ....utils.chromatogram import AgilentChannelChromatogramData
from ....utils.table_types import Table


class MassSpecController(TableController):

    def __init__(self, controller: CommunicationController, src: str, data_dir: str, table: Table):
        super().__init__(controller, src, data_dir, table)

    def get_row(self, row: int):
        pass

    def retrieve_recent_data_files(self):
        pass

    def get_data(self) -> Union[list[AgilentChannelChromatogramData], AgilentChannelChromatogramData]:
        pass
