"""
Module to provide API for higher-level HPLC actions.

Authors: Lucy Hao
"""

from typing import Union, Optional

from .controllers.devices.injector import InjectorController
from ..control.controllers import MethodController, SequenceController, CommunicationController
from ..utils.chromatogram import AgilentChannelChromatogramData
from ..utils.injector_types import InjectorTable
from ..utils.macro import Command, HPLCRunningStatus, HPLCAvailStatus, HPLCErrorStatus, Response
from ..utils.method_types import MethodDetails
from ..utils.sequence_types import SequenceTable, SequenceEntry
from ..utils.table_types import Table


class HPLCController:
    # tables
    METHOD_TIMETABLE = Table(
        register="RCPMP1Method[1]",
        name="Timetable"
    )

    SEQUENCE_TABLE = Table(
        register="_sequence[1]",
        name="SeqTable1"
    )

    INJECTOR_TABLE = Table(
        register="RCWLS1Pretreatment[1]",
        name="InstructionTable"
    )

    MSD_TABLE = Table(
        register="MSACQINFO[1]",
        name="SprayChamber"
    )

    def __init__(self,
                 comm_dir: str,
                 data_dir: str,
                 method_dir: str,
                 sequence_dir: str,
                 offline: bool = False):
        """Initialize HPLC controller. The `hplc_talk.mac` macro file must be loaded in the Chemstation software.
        `comm_dir` must match the file path in the macro file.

        :param comm_dir: Name of directory for communication, where ChemStation will read and write from. Can be any existing directory.
        :raises FileNotFoundError: If either `data_dir`, `method_dir`, `sequence_dir`, or `comm_dir` is not a valid directory.
        """
        self.comm = CommunicationController(comm_dir=comm_dir) if not offline else None
        self.method_controller = MethodController(controller=self.comm,
                                                  src=method_dir,
                                                  data_dir=data_dir,
                                                  table=self.METHOD_TIMETABLE,
                                                  offline=offline,
                                                  injector_controller=InjectorController(controller=self.comm,
                                                                                         table=self.INJECTOR_TABLE,
                                                                                         offline=offline))
        self.sequence_controller = SequenceController(controller=self.comm,
                                                      src=sequence_dir,
                                                      data_dir=data_dir,
                                                      table=self.SEQUENCE_TABLE,
                                                      method_dir=method_dir,
                                                      offline=offline)

    def send(self, cmd: Union[Command, str]):
        if not self.comm:
            raise RuntimeError(
                "Communication controller must be initialized before sending command. It is currently in offline mode.")
        self.comm.send(cmd)

    def receive(self) -> Response:
        if not self.comm:
            raise RuntimeError(
                "Communication controller must be initialized before sending command. It is currently in offline mode.")
        return self.comm.receive().value

    def status(self) -> Union[HPLCRunningStatus | HPLCAvailStatus | HPLCErrorStatus]:
        if not self.comm:
            raise RuntimeError(
                "Communication controller must be initialized before sending command. It is currently in offline mode.")
        return self.comm.get_status()

    def switch_method(self, method_name: str):
        """
        Allows the user to switch between pre-programmed methods. No need to append '.M'
        to the end of the method name. For example. for the method named 'General-Poroshell.M',
        only 'General-Poroshell' is needed.

        :param method_name: any available method in Chemstation method directory
        :raises  IndexError: Response did not have expected format. Try again.
        :raises  AssertionError: The desired method is not selected. Try again.
        """
        self.method_controller.switch(method_name)

    def switch_sequence(self, sequence_name: str):
        """
         Allows the user to switch between pre-programmed sequences. The sequence name does not need the '.S' extension.
         For example. for the method named 'mySeq.S', only 'mySeq' is needed.

        :param sequence_name: The name of the sequence file
        """
        self.sequence_controller.switch(sequence_name)

    def run_method(self, experiment_name: str, stall_while_running: bool = True):
        """
        This is the preferred method to trigger a run.
        Starts the currently selected method, storing data
        under the <data_dir>/<experiment_name>.D folder.
        The <experiment_name> will be appended with a timestamp in the '%Y-%m-%d-%H-%M' format.
        Device must be ready.

        :param experiment_name: Name of the experiment
        :param stall_while_running: whether this method should return or stall while HPLC runs.
        """
        self.method_controller.run(experiment_name, stall_while_running)

    def run_sequence(self, stall_while_running: bool = True):
        """
        Starts the currently loaded sequence, storing data
        under the <data_dir>/<sequence table name> folder.
        Device must be ready.

        :param stall_while_running: whether this method should return or stall while HPLC runs.
        """
        self.sequence_controller.run(stall_while_running=stall_while_running)

    def edit_method(self, updated_method: MethodDetails, save: bool = False):
        """Updated the currently loaded method in ChemStation with provided values.

        :param updated_method: the method with updated values, to be sent to Chemstation to modify the currently loaded method.
        :param save: whether this method should be to disk, or just modified.
        """
        self.method_controller.edit(updated_method, save)

    def edit_sequence(self, updated_sequence: SequenceTable):
        """
        Updates the currently loaded sequence table with the provided table.
        If you would only like to edit a single row of a sequence table, use `edit_sequence_row` instead.

        :param updated_sequence: The sequence table to be written to the currently loaded sequence table.
        """
        self.sequence_controller.edit(updated_sequence)

    def edit_sequence_row(self, row: SequenceEntry, num: int):
        """
        Edits a row in the sequence table. Assumes the row already exists.

        :param row: sequence row entry with updated information
        :param num: the row to edit, based on 1-based indexing
        """
        self.sequence_controller.edit_row(row, num)

    def get_last_run_method_data(self, read_uv: bool = False,
                                 data: Optional[str] = None) -> AgilentChannelChromatogramData:
        """
        Returns the last run method data.

        :param data: If you want to just load method data but from a file path. This file path must be the complete file path.
        :param read_uv: whether to also read the UV file
        """
        return self.method_controller.get_data(custom_path=data, read_uv=read_uv)

    def get_last_run_sequence_data(self, read_uv: bool = False,
                                   data: Optional[str] = None) -> list[AgilentChannelChromatogramData]:
        """
        Returns data for all rows in the last run sequence data.

        :param data: If you want to just load sequence data but from a file path. This file path must be the complete file path.
        :param read_uv: whether to also read the UV file
        """
        return self.sequence_controller.get_data(custom_path=data, read_uv=read_uv)

    def check_loaded_sequence(self) -> str:
        """
        Returns the name of the currently loaded sequence.
        """
        return self.sequence_controller.check()

    def check_loaded_method(self) -> str:
        """
        Returns the name of the currently loaded method.
        """
        return self.method_controller.check()

    def load_injector_program(self) -> InjectorTable:
        return self.method_controller.injector_controller.load()

    def load_method(self) -> MethodDetails:
        """
        Returns all details of the currently loaded method, including its timetable.
        """
        return self.method_controller.load()

    def load_sequence(self) -> SequenceTable:
        """
        Returns the currently loaded sequence.
        """
        return self.sequence_controller.load()

    def standby(self):
        """Switches all modules in standby mode. All lamps and pumps are switched off."""
        self.send(Command.STANDBY_CMD)

    def preprun(self):
        """ Prepares all modules for run. All lamps and pumps are switched on."""
        self.send(Command.PREPRUN_CMD)

    def lamp_on(self):
        """Turns the UV lamp on."""
        self.send(Command.LAMP_ON_CMD)

    def lamp_off(self):
        """Turns the UV lamp off."""
        self.send(Command.LAMP_OFF_CMD)

    def pump_on(self):
        """Turns on the pump on."""
        self.send(Command.PUMP_ON_CMD)

    def pump_off(self):
        """Turns the pump off."""
        self.send(Command.PUMP_OFF_CMD)

    def instrument_off(self):
        """Shuts the entire instrument off, including pumps, lamps, thermostat."""
        self.send(Command.INSTRUMENT_OFF)

    def instrument_on(self):
        """Turns the entire instrument on, including pumps, lamps, thermostat."""
        self.send(Command.INSTRUMENT_ON)
