from ....control.controllers import CommunicationController
from .device import DeviceController
from ....utils.pump_types import Pump
from ....utils.table_types import Table


class PumpController(DeviceController):

    def __init__(self, controller: CommunicationController, table: Table):
        super().__init__(controller, table)
        self.A1 = Pump(in_use=True, solvent="A1")
        self.B1 = Pump(in_use=True, solvent="B1")
        self.A2 = Pump(in_use=False, solvent="A2")
        self.B2 = Pump(in_use=False, solvent="B2")

    def validate_pumps(self):
        invalid_A_pump_usage = self.A1.in_use and self.A2.in_use
        invalid_B_pump_usage = self.B1.in_use and self.B2.in_use
        if invalid_A_pump_usage or invalid_B_pump_usage:
            raise AttributeError

    def switch_pump(self, num: int, pump: str):
        if pump == "A":
            if num == 1:
                self.A1.in_use = True
                self.A2.in_use = False
            elif num == 2:
                self.A1.in_use = False
                self.A2.in_use = True
        elif pump == "B":
            if num == 1:
                self.B1.in_use = True
                self.B2.in_use = False
            elif num == 2:
                self.B1.in_use = False
                self.B2.in_use = True
        self.purge()

    def purge(self):
        pass

    def get_row(self, row: int):
        pass
