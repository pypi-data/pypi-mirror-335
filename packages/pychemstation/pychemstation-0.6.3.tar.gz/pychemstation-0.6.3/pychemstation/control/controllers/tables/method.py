import os
import time

from xsdata.formats.dataclass.parsers import XmlParser

from .table import TableController
from ..devices.injector import InjectorController
from ....control.controllers import CommunicationController
from ....generated import PumpMethod, DadMethod, SolventElement
from ....utils.chromatogram import TIME_FORMAT, AgilentChannelChromatogramData
from ....utils.macro import *
from ....utils.method_types import *
from ....utils.table_types import *


class MethodController(TableController):
    """
    Class containing method related logic
    """

    def __init__(self, controller: CommunicationController,
                 src: str,
                 data_dir: str,
                 table: Table,
                 offline: bool,
                 injector_controller: InjectorController):
        self.injector_controller = injector_controller
        super().__init__(controller, src, data_dir, table, offline=offline)

    def check(self) -> str:
        time.sleep(2)
        self.send(Command.GET_METHOD_CMD)
        time.sleep(2)
        res = self.receive()
        if res.is_ok():
            return res.ok_value.string_response
        return "ERROR"

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
        )

    def get_row(self, row: int) -> TimeTableEntry:
        flow = None
        om = None

        try:
            flow = self.get_num(row, RegisterFlag.TIMETABLE_FLOW)
        except RuntimeError:
            pass
        try:
            om = self.get_num(row, RegisterFlag.TIMETABLE_SOLVENT_B_COMPOSITION)
        except RuntimeError:
            pass

        return TimeTableEntry(start_time=self.get_num(row, RegisterFlag.TIME),
                              organic_modifer=om,
                              flow=flow)

    def get_timetable(self, rows: int):
        uncoalesced_timetable_rows = [self.get_row(r + 1) for r in range(rows)]
        timetable_rows = {}
        for row in uncoalesced_timetable_rows:
            time_key = str(row.start_time)
            if time_key not in timetable_rows.keys():
                timetable_rows[time_key] = TimeTableEntry(start_time=row.start_time,
                                                          flow=row.flow,
                                                          organic_modifer=row.organic_modifer)
            else:
                if row.flow:
                    timetable_rows[time_key].flow = row.flow
                if row.organic_modifer:
                    timetable_rows[time_key].organic_modifer = row.organic_modifer
        entries = list(timetable_rows.values())
        entries.sort(key=lambda e: e.start_time)
        return entries

    def load(self) -> MethodDetails:
        rows = self.get_num_rows()
        if rows.is_ok():
            self.send(Command.GET_METHOD_CMD)
            res = self.receive()
            method_name = res.ok_value.string_response
            timetable_rows = self.get_timetable(int(rows.ok_value.num_response))
            params = self.get_method_params()
            stop_time = self.controller.get_num_val(
                cmd=TableOperation.GET_OBJ_HDR_VAL.value.format(
                    register=self.table.register,
                    register_flag=RegisterFlag.MAX_TIME))
            post_time = self.controller.get_num_val(
                cmd=TableOperation.GET_OBJ_HDR_VAL.value.format(
                    register=self.table.register,
                    register_flag=RegisterFlag.POST_TIME))
            self.table_state = MethodDetails(name=method_name,
                                             timetable=timetable_rows,
                                             stop_time=stop_time,
                                             post_time=post_time,
                                             params=params)
            return self.table_state
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
        self.send(Command.SWITCH_METHOD_CMD_SPECIFIC.value.format(method_dir=self.src,
                                                         method_name=method_name))

        time.sleep(2)
        self.send(Command.GET_METHOD_CMD)
        time.sleep(2)
        res = self.receive()
        if res.is_ok():
            parsed_response = res.ok_value.string_response
            assert parsed_response == f"{method_name}.M", "Switching Methods failed."
        self.table_state = None

    def load_from_disk(self, method_name: str) -> MethodDetails:
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

            self.table_state = MethodDetails(name=method_name,
                                             params=HPLCMethodParams(organic_modifier=organic_modifier.percentage,
                                                                     flow=method.flow),
                                             stop_time=method.stop_time.stop_time_value,
                                             post_time=method.post_time.post_time_value,
                                             timetable=[TimeTableEntry(start_time=tte.time,
                                                                       organic_modifer=tte.percent_b,
                                                                       flow=method.flow
                                                                       ) for tte in method.timetable.timetable_entry],
                                             dad_wavelengthes=dad.signals.signal)
            return self.table_state
        else:
            raise FileNotFoundError

    def edit(self, updated_method: MethodDetails, save: bool):
        """Updated the currently loaded method in ChemStation with provided values.

        :param updated_method: the method with updated values, to be sent to Chemstation to modify the currently loaded method.
        :param save: if false only modifies the method, otherwise saves to disk
        """
        self.table_state = updated_method
        initial_organic_modifier: Param = Param(val=updated_method.params.organic_modifier,
                                                chemstation_key=RegisterFlag.SOLVENT_B_COMPOSITION,
                                                ptype=PType.NUM)
        max_time: Param = Param(val=updated_method.stop_time,
                                chemstation_key=RegisterFlag.MAX_TIME,
                                ptype=PType.NUM)
        post_time: Param = Param(val=updated_method.post_time,
                                 chemstation_key=RegisterFlag.POST_TIME,
                                 ptype=PType.NUM)
        flow: Param = Param(val=updated_method.params.flow,
                            chemstation_key=RegisterFlag.FLOW,
                            ptype=PType.NUM)

        # Method settings required for all runs
        self.update_method_params(flow, initial_organic_modifier, max_time, post_time)
        self._update_method_timetable(updated_method.timetable)

        if save:
            self.send(Command.SAVE_METHOD_CMD.value.format(
                commit_msg=f"saved method at {str(time.time())}"
            ))

    def update_method_params(self, flow, initial_organic_modifier, max_time, post_time):
        self.delete_table()
        self._update_param(initial_organic_modifier)
        self._update_param(flow)
        if self.table_state.stop_time:
            self._update_param(Param(val="Set", chemstation_key=RegisterFlag.STOPTIME_MODE, ptype=PType.STR))
            self._update_param(max_time)
        else:
            self._update_param(Param(val="Off", chemstation_key=RegisterFlag.STOPTIME_MODE, ptype=PType.STR))
        if self.table_state.post_time:
            self._update_param(Param(val="Set", chemstation_key=RegisterFlag.POSTIME_MODE, ptype=PType.STR))
            self._update_param(post_time)
        else:
            self._update_param(Param(val="Off", chemstation_key=RegisterFlag.POSTIME_MODE, ptype=PType.STR))
        self.download()

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

    def download(self):
        self.send('Sleep 1')
        self.sleepy_send("DownloadRCMethod PMP1")
        self.send('Sleep 1')

    def edit_row(self, row: TimeTableEntry, first_row: bool = False):
        if first_row:
            if row.organic_modifer:
                self.add_row()
                self.add_new_col_text(col_name=RegisterFlag.FUNCTION, val=RegisterFlag.SOLVENT_COMPOSITION.value)
                self.add_new_col_num(col_name=RegisterFlag.TIME, val=row.start_time)
                self.add_new_col_num(col_name=RegisterFlag.TIMETABLE_SOLVENT_B_COMPOSITION, val=row.organic_modifer)
            if row.flow:
                self.add_row()
                self.get_num_rows()
                self.edit_row_text(col_name=RegisterFlag.FUNCTION, val=RegisterFlag.FLOW.value)
                self.add_new_col_num(col_name=RegisterFlag.TIMETABLE_FLOW, val=row.flow)
                self.edit_row_num(col_name=RegisterFlag.TIMETABLE_FLOW, val=row.flow)
            self.download()
        else:
            if row.organic_modifer:
                self.add_row()
                self.get_num_rows()
                self.edit_row_text(col_name=RegisterFlag.FUNCTION, val=RegisterFlag.SOLVENT_COMPOSITION.value)
                self.edit_row_num(col_name=RegisterFlag.TIME, val=row.start_time)
                self.edit_row_num(col_name=RegisterFlag.TIMETABLE_SOLVENT_B_COMPOSITION, val=row.organic_modifer)
                self.download()
            if row.flow:
                self.add_row()
                self.get_num_rows()
                self.edit_row_text(col_name=RegisterFlag.FUNCTION, val=RegisterFlag.FLOW.value)
                self.edit_row_num(col_name=RegisterFlag.TIMETABLE_FLOW, val=row.flow)
                self.edit_row_num(col_name=RegisterFlag.TIME, val=row.start_time)
                self.download()

    def _update_method_timetable(self, timetable_rows: list[TimeTableEntry]):
        self.get_num_rows()

        self.delete_table()
        res = self.get_num_rows()
        while not res.is_err():
            self.delete_table()
            res = self.get_num_rows()

        self.new_table()
        self.get_num_rows()

        for i, row in enumerate(timetable_rows):
            self.edit_row(row=row, first_row=i == 0)

    def stop(self):
        """
        Stops the method run. A dialog window will pop up and manual intervention may be required.\
        """
        self.send(Command.STOP_METHOD_CMD)

    def run(self, experiment_name: str, stall_while_running: bool = True):
        """
        This is the preferred method to trigger a run.
        Starts the currently selected method, storing data
        under the <data_dir>/<experiment_name>.D folder.
        The <experiment_name> will be appended with a timestamp in the '%Y-%m-%d-%H-%M' format.
        Device must be ready.

        :param experiment_name: Name of the experiment
        """

        folder_name = ""
        hplc_is_running = False
        tries = 0
        while tries < 10 and not hplc_is_running:
            timestamp = time.strftime(TIME_FORMAT)
            self.send(Command.RUN_METHOD_CMD.value.format(data_dir=self.data_dir,
                                                          experiment_name=experiment_name,
                                                          timestamp=timestamp))
            folder_name = f"{experiment_name}_{timestamp}.D"
            hplc_is_running = self.check_hplc_is_running()
            tries += 1

        if not hplc_is_running:
            raise RuntimeError("Method failed to start.")

        self.data_files.append(os.path.join(self.data_dir, folder_name))

        if stall_while_running:

            if not self.table_state:
                self.table_state = self.load()

            run_completed = self.check_hplc_done_running(method=self.table_state)
            if run_completed.is_ok():
                self.data_files[-1] = run_completed.ok_value
            else:
                raise RuntimeError("Run error has occurred.")
        else:
            self.data_files[-1] = self.fuzzy_match_most_recent_folder(folder_name).ok_value

    def retrieve_recent_data_files(self) -> str:
        return self.data_files[-1]

    def get_data(self, custom_path: Optional[str] = None,
                 read_uv: bool = False) -> AgilentChannelChromatogramData:
        if not custom_path:
            self.get_spectrum(self.data_files[-1], read_uv)
        else:
            self.get_spectrum(custom_path, read_uv)
        return AgilentChannelChromatogramData(**self.spectra) if not read_uv else self.uv
