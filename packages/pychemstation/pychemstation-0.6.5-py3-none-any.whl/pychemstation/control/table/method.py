import os
import time
from typing import Optional, Any

from xsdata.formats.dataclass.parsers import XmlParser

from .. import CommunicationController
from ...control.table.table_controller import TableController
from ...generated import PumpMethod, DadMethod, SolventElement
from ...utils.chromatogram import TIME_FORMAT, AgilentHPLCChromatogram
from ...utils.macro import Command
from ...utils.method_types import PType, TimeTableEntry, Param, MethodTimetable, HPLCMethodParams
from ...utils.table_types import RegisterFlag, TableOperation, Table


class MethodController(TableController):
    """
    Class containing method related logic
    """

    def __init__(self, controller: CommunicationController, src: str, data_dir: str, table: Table):
        super().__init__(controller, src, data_dir, table)

    def get_method_params(self) -> HPLCMethodParams:
        return HPLCMethodParams(organic_modifier=self.controller.get_num_val(
            cmd=TableOperation.GET_OBJ_HDR_VAL.value.format(
                register=self.table.register,
                register_flag=RegisterFlag.SOLVENT_B_COMPOSITION
            )
        ),
            flow=self.controller.get_num_val(
                cmd=TableOperation.GET_OBJ_HDR_VAL.value.format(
                    register=self.table.register,
                    register_flag=RegisterFlag.FLOW
                )
            ),
            maximum_run_time=self.controller.get_num_val(
                cmd=TableOperation.GET_OBJ_HDR_VAL.value.format(
                    register=self.table.register,
                    register_flag=RegisterFlag.MAX_TIME
                )
            ),
        )

    def get_row(self, row: int) -> TimeTableEntry:
        return TimeTableEntry(start_time=self.get_num(row, RegisterFlag.TIME),
                              organic_modifer=self.get_num(row, RegisterFlag.TIMETABLE_SOLVENT_B_COMPOSITION),
                              flow=None)

    def load(self) -> MethodTimetable:
        rows = self.get_num_rows()
        if rows.is_ok():
            timetable_rows = [self.get_row(r + 1) for r in range(int(rows.ok_value.num_response))]
            return MethodTimetable(
                first_row=self.get_method_params(),
                subsequent_rows=timetable_rows)
        else:
            raise RuntimeError(rows.err_value)

    def current_method(self, method_name: str):
        """
        Checks if a given method is already loaded into Chemstation. Method name does not need the ".M" extension.

        :param method_name: a Chemstation method
        :return: True if method is already loaded
        """
        self.send(Command.GET_METHOD_CMD)
        parsed_response = self.receive()
        return method_name in parsed_response

    def switch(self, method_name: str):
        """
        Allows the user to switch between pre-programmed methods. No need to append '.M'
        to the end of the method name. For example. for the method named 'General-Poroshell.M',
        only 'General-Poroshell' is needed.

        :param method_name: any available method in Chemstation method directory
        :raise IndexError: Response did not have expected format. Try again.
        :raise AssertionError: The desired method is not selected. Try again.
        """
        self.send(Command.SWITCH_METHOD_CMD.value.format(method_dir=self.src,
                                                         method_name=method_name))

        time.sleep(2)
        self.send(Command.GET_METHOD_CMD)
        time.sleep(2)
        res = self.receive()
        if res.is_ok():
            parsed_response = res.ok_value.string_response
            assert parsed_response == f"{method_name}.M", "Switching Methods failed."

    def load_from_disk(self, method_name: str) -> MethodTimetable:
        """
        Retrieve method details of an existing method. Don't need to append ".M" to the end. This assumes the
        organic modifier is in Channel B and that Channel A contains the aq layer. Additionally, assumes
         only two solvents are being used.

        :param method_name: name of method to load details of
        :raises FileNotFoundError: Method does not exist
        :return: method details
        """
        method_folder = f"{method_name}.M"
        method_path = os.path.join(self.src, method_folder, "AgilentPumpDriver1.RapidControl.MethodXML.xml")
        dad_path = os.path.join(self.src, method_folder, "Agilent1200erDadDriver1.RapidControl.MethodXML.xml")

        if os.path.exists(os.path.join(self.src, f"{method_name}.M")):
            parser = XmlParser()
            method = parser.parse(method_path, PumpMethod)
            dad = parser.parse(dad_path, DadMethod)

            organic_modifier: Optional[SolventElement] = None
            aq_modifier: Optional[SolventElement] = None

            if len(method.solvent_composition.solvent_element) == 2:
                for solvent in method.solvent_composition.solvent_element:
                    if solvent.channel == "Channel_A":
                        aq_modifier = solvent
                    elif solvent.channel == "Channel_B":
                        organic_modifier = solvent

            return MethodTimetable(
                first_row=HPLCMethodParams(
                    organic_modifier=organic_modifier.percentage,
                    flow=method.flow,
                    maximum_run_time=method.stop_time,
                    temperature=-1),
                subsequent_rows=[
                    TimeTableEntry(
                        start_time=tte.time,
                        organic_modifer=tte.percent_b,
                        flow=method.flow
                    ) for tte in method.timetable.timetable_entry
                ],
                dad_wavelengthes=dad.signals.signal,
                organic_modifier=organic_modifier,
                modifier_a=aq_modifier
            )
        else:
            raise FileNotFoundError

    def edit(self, updated_method: MethodTimetable, save: bool):
        """Updated the currently loaded method in ChemStation with provided values.

        :param updated_method: the method with updated values, to be sent to Chemstation to modify the currently loaded method.
        """
        initial_organic_modifier: Param = Param(val=updated_method.first_row.organic_modifier,
                                                chemstation_key=RegisterFlag.SOLVENT_B_COMPOSITION,
                                                ptype=PType.NUM)
        max_time: Param = Param(val=updated_method.first_row.maximum_run_time,
                                chemstation_key=RegisterFlag.MAX_TIME,
                                ptype=PType.NUM)
        flow: Param = Param(val=updated_method.first_row.flow,
                            chemstation_key=RegisterFlag.FLOW,
                            ptype=PType.NUM)

        # Method settings required for all runs
        self.delete_table()
        self._update_param(initial_organic_modifier)
        self._update_param(flow)
        self._update_param(Param(val="Set",
                                 chemstation_key=RegisterFlag.STOPTIME_MODE,
                                 ptype=PType.STR))
        self._update_param(max_time)
        self._update_param(Param(val="Off",
                                 chemstation_key=RegisterFlag.POSTIME_MODE,
                                 ptype=PType.STR))

        self.send("DownloadRCMethod PMP1")

        self._update_method_timetable(updated_method.subsequent_rows)

        if save:
            self.send(Command.SAVE_METHOD_CMD.value.format(
                commit_msg=f"saved method at {str(time.time())}"
            ))

    def _update_method_timetable(self, timetable_rows: list[TimeTableEntry]):
        self.sleepy_send('Local Rows')
        self.get_num_rows()

        self.sleepy_send('DelTab RCPMP1Method[1], "Timetable"')
        res = self.get_num_rows()
        while not res.is_err():
            self.sleepy_send('DelTab RCPMP1Method[1], "Timetable"')
            res = self.get_num_rows()

        self.sleepy_send('NewTab RCPMP1Method[1], "Timetable"')
        self.get_num_rows()

        for i, row in enumerate(timetable_rows):
            if i == 0:
                self.send('Sleep 1')
                self.sleepy_send('InsTabRow RCPMP1Method[1], "Timetable"')
                self.send('Sleep 1')

                self.sleepy_send('NewColText RCPMP1Method[1], "Timetable", "Function", "SolventComposition"')
                self.sleepy_send(f'NewColVal RCPMP1Method[1], "Timetable", "Time", {row.start_time}')
                self.sleepy_send(
                    f'NewColVal RCPMP1Method[1], "Timetable", "SolventCompositionPumpChannel2_Percentage", {row.organic_modifer}')

                self.send('Sleep 1')
                self.sleepy_send("DownloadRCMethod PMP1")
                self.send('Sleep 1')
            else:
                self.sleepy_send('InsTabRow RCPMP1Method[1], "Timetable"')
                self.get_num_rows()

                self.sleepy_send(
                    f'SetTabText RCPMP1Method[1], "Timetable", Rows, "Function", "SolventComposition"')
                self.sleepy_send(
                    f'SetTabVal RCPMP1Method[1], "Timetable", Rows, "Time", {row.start_time}')
                self.sleepy_send(
                    f'SetTabVal RCPMP1Method[1], "Timetable", Rows, "SolventCompositionPumpChannel2_Percentage", {row.organic_modifer}')

                self.send("Sleep 1")
                self.sleepy_send("DownloadRCMethod PMP1")
                self.send("Sleep 1")
                self.get_num_rows()

    def _update_param(self, method_param: Param):
        """Change a method parameter, changes what is visibly seen in Chemstation GUI.
         (changes the first row in the timetable)

        :param method_param: a parameter to update for currently loaded method.
        """
        register = self.table.register
        setting_command = TableOperation.UPDATE_OBJ_HDR_VAL if method_param.ptype == PType.NUM else TableOperation.UPDATE_OBJ_HDR_TEXT
        if isinstance(method_param.chemstation_key, list):
            for register_flag in method_param.chemstation_key:
                self.send(setting_command.value.format(register=register,
                                                       register_flag=register_flag,
                                                       val=method_param.val))
        else:
            self.send(setting_command.value.format(register=register,
                                                   register_flag=method_param.chemstation_key,
                                                   val=method_param.val))
        time.sleep(2)

    def stop(self):
        """
        Stops the method run. A dialog window will pop up and manual intervention may be required.\
        """
        self.send(Command.STOP_METHOD_CMD)

    def run(self, experiment_name: str):
        """
        This is the preferred method to trigger a run.
        Starts the currently selected method, storing data
        under the <data_dir>/<experiment_name>.D folder.
        The <experiment_name> will be appended with a timestamp in the '%Y-%m-%d-%H-%M' format.
        Device must be ready.

        :param experiment_name: Name of the experiment
        """
        timestamp = time.strftime(TIME_FORMAT)
        self.send(Command.RUN_METHOD_CMD.value.format(data_dir=self.data_dir,
                                                      experiment_name=experiment_name,
                                                      timestamp=timestamp))

        if self.check_hplc_is_running():
            folder_name = f"{experiment_name}_{timestamp}.D"
            self.data_files.append(os.path.join(self.data_dir, folder_name))

        run_completed = self.check_hplc_done_running()

        if not run_completed.is_ok():
            raise RuntimeError("Run did not complete as expected")

    def retrieve_recent_data_files(self) -> str:
        return self.data_files[-1]

    def get_data(self) -> dict[str, AgilentHPLCChromatogram]:
        self.get_spectrum(self.data_files[-1])
        return self.spectra
