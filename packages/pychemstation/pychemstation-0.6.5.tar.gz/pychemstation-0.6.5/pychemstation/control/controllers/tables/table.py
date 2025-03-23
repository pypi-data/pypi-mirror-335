"""
Abstract module containing shared logic for Method and Sequence tables.

Authors: Lucy Hao
"""

import abc
import os
import warnings
from dataclasses import dataclass
from typing import Union, Optional, AnyStr

import numpy as np
import polling
import rainbow as rb
from result import Result, Ok, Err

from ....control.controllers.comm import CommunicationController
from ....utils.chromatogram import AgilentHPLCChromatogram, AgilentChannelChromatogramData
from ....utils.macro import Command, HPLCRunningStatus, Response
from ....utils.method_types import MethodDetails
from ....utils.sequence_types import SequenceDataFiles, SequenceTable
from ....utils.table_types import Table, TableOperation, RegisterFlag

TableType = Union[MethodDetails, SequenceTable]


@dataclass
class ChromData:
    x: np.array
    y: np.array


class TableController(abc.ABC):

    def __init__(self, controller: CommunicationController,
                 src: Optional[str],
                 data_dir: Optional[str],
                 table: Table,
                 offline: bool = False):
        self.controller = controller
        self.table = table
        self.table_state: Optional[TableType] = None

        if not offline:
            # Initialize row counter for table operations
            self.send('Local Rows')

            if src and os.path.isdir(src):
                self.src: str = src
            elif isinstance(src, str):
                raise FileNotFoundError(f"dir: {src} not found.")

            if data_dir and os.path.isdir(data_dir):
                self.data_dir: str = data_dir
            elif isinstance(data_dir, str):
                raise FileNotFoundError(f"dir: {data_dir} not found.")

            if hasattr(self, "data_dir"):
                self.spectra: dict[str, Optional[AgilentHPLCChromatogram]] = {
                    "A": AgilentHPLCChromatogram(self.data_dir),
                    "B": AgilentHPLCChromatogram(self.data_dir),
                    "C": AgilentHPLCChromatogram(self.data_dir),
                    "D": AgilentHPLCChromatogram(self.data_dir),
                    "E": AgilentHPLCChromatogram(self.data_dir),
                    "F": AgilentHPLCChromatogram(self.data_dir),
                    "G": AgilentHPLCChromatogram(self.data_dir),
                    "H": AgilentHPLCChromatogram(self.data_dir),
                }
        else:
            self.spectra: dict[str, Optional[AgilentHPLCChromatogram]] = {
                "A": AgilentHPLCChromatogram(),
                "B": AgilentHPLCChromatogram(),
                "C": AgilentHPLCChromatogram(),
                "D": AgilentHPLCChromatogram(),
                "E": AgilentHPLCChromatogram(),
                "F": AgilentHPLCChromatogram(),
                "G": AgilentHPLCChromatogram(),
                "H": AgilentHPLCChromatogram(),
            }
        self.data_files: Union[list[SequenceDataFiles], list[str]] = []

        self.uv = None

    def receive(self) -> Result[Response, str]:
        for _ in range(10):
            try:
                return self.controller.receive()
            except IndexError:
                continue
        return Err("Could not parse response")

    def send(self, cmd: Union[Command, str]):
        if not self.controller:
            raise RuntimeError(
                "Communication controller must be initialized before sending command. It is currently in offline mode.")
        self.controller.send(cmd)

    def sleepy_send(self, cmd: Union[Command, str]):
        self.controller.sleepy_send(cmd)

    def sleep(self, seconds: int):
        """
        Tells the HPLC to wait for a specified number of seconds.

        :param seconds: number of seconds to wait
        """
        self.send(Command.SLEEP_CMD.value.format(seconds=seconds))

    def get_num(self, row: int, col_name: RegisterFlag) -> Union[int, float]:
        return self.controller.get_num_val(TableOperation.GET_ROW_VAL.value.format(register=self.table.register,
                                                                                   table_name=self.table.name,
                                                                                   row=row,
                                                                                   col_name=col_name.value))

    def get_text(self, row: int, col_name: RegisterFlag) -> str:
        return self.controller.get_text_val(TableOperation.GET_ROW_TEXT.value.format(register=self.table.register,
                                                                                     table_name=self.table.name,
                                                                                     row=row,
                                                                                     col_name=col_name.value))

    def add_new_col_num(self,
                        col_name: RegisterFlag,
                        val: Union[int, float]):
        self.sleepy_send(TableOperation.NEW_COL_VAL.value.format(
            register=self.table.register,
            table_name=self.table.name,
            col_name=col_name,
            val=val))

    def add_new_col_text(self,
                         col_name: RegisterFlag,
                         val: str):
        self.sleepy_send(TableOperation.NEW_COL_TEXT.value.format(
            register=self.table.register,
            table_name=self.table.name,
            col_name=col_name,
            val=val))

    def edit_row_num(self,
                     col_name: RegisterFlag,
                     val: Union[int, float],
                     row: Optional[int] = None):
        self.sleepy_send(TableOperation.EDIT_ROW_VAL.value.format(
            register=self.table.register,
            table_name=self.table.name,
            row=row if row is not None else 'Rows',
            col_name=col_name,
            val=val))

    def edit_row_text(self,
                      col_name: RegisterFlag,
                      val: str,
                      row: Optional[int] = None):
        self.sleepy_send(TableOperation.EDIT_ROW_TEXT.value.format(
            register=self.table.register,
            table_name=self.table.name,
            row=row if row is not None else 'Rows',
            col_name=col_name,
            val=val))

    @abc.abstractmethod
    def get_row(self, row: int):
        pass

    def delete_row(self, row: int):
        self.sleepy_send(TableOperation.DELETE_ROW.value.format(register=self.table.register,
                                                                table_name=self.table.name,
                                                                row=row))

    def add_row(self):
        """
        Adds a row to the provided table for currently loaded method or sequence.
        Import either the SEQUENCE_TABLE or METHOD_TIMETABLE from hein_analytical_control.constants.
        You can also provide your own table.

        :param table: the table to add a new row to
        """
        self.sleepy_send(TableOperation.NEW_ROW.value.format(register=self.table.register,
                                                             table_name=self.table.name))

    def delete_table(self):
        """
        Deletes the table for the current loaded method or sequence.
        Import either the SEQUENCE_TABLE or METHOD_TIMETABLE from hein_analytical_control.constants.
        You can also provide your own table.

        :param table: the table to delete
        """
        self.sleepy_send(TableOperation.DELETE_TABLE.value.format(register=self.table.register,
                                                                  table_name=self.table.name))

    def new_table(self):
        """
        Creates the table for the currently loaded method or sequence. Import either the SEQUENCE_TABLE or
        METHOD_TIMETABLE from hein_analytical_control.constants. You can also provide your own table.

        :param table: the table to create
        """
        self.send(TableOperation.CREATE_TABLE.value.format(register=self.table.register,
                                                           table_name=self.table.name))

    def get_num_rows(self) -> Result[Response, str]:
        self.send(TableOperation.GET_NUM_ROWS.value.format(register=self.table.register,
                                                           table_name=self.table.name,
                                                           col_name=RegisterFlag.NUM_ROWS))
        self.send(Command.GET_ROWS_CMD.value.format(register=self.table.register,
                                                    table_name=self.table.name,
                                                    col_name=RegisterFlag.NUM_ROWS))
        res = self.controller.receive()

        if res.is_ok():
            self.send("Sleep 0.1")
            self.send('Print Rows')
            return res
        else:
            return Err("No rows could be read.")

    def check_hplc_is_running(self) -> bool:
        try:
            started_running = polling.poll(lambda: isinstance(self.controller.get_status(), HPLCRunningStatus),
                                           step=3, max_tries=10)
        except Exception as e:
            print(e)
            return False
        return started_running

    def check_hplc_done_running(self,
                                method: Optional[MethodDetails] = None,
                                sequence: Optional[SequenceTable] = None) -> Result[str, str]:
        """
        Checks if ChemStation has finished running and can read data back

        :param method: if you are running a method and want to read back data, the timeout period will be adjusted to be longer than the method's runtime
        :param sequence: if you are running a sequence and want to read back data, the timeout period will be adjusted to be longer than the sequence's runtime
        :return: Return True if data can be read back, else False.
        """
        timeout = 10 * 60
        if method:
            timeout = ((method.stop_time + method.post_time + 3) * 60)
        if sequence:
            timeout *= len(sequence.rows)

        most_recent_folder = self.retrieve_recent_data_files()

        finished_run = False
        try:
            finished_run = polling.poll(
                lambda: self.controller.check_if_running(),
                timeout=timeout,
                step=50)
        except Exception:
            pass

        check_folder = self.fuzzy_match_most_recent_folder(most_recent_folder)
        if check_folder.is_ok() and finished_run:
            return check_folder
        elif check_folder.is_ok():
            finished_run = polling.poll(
                lambda: self.controller.check_if_running(),
                timeout=timeout,
                step=50)
            if finished_run:
                return check_folder
            return check_folder
        else:
            return Err("Run did not complete as expected")

    def fuzzy_match_most_recent_folder(self, most_recent_folder) -> Result[str, str]:
        if os.path.exists(most_recent_folder):
            return Ok(most_recent_folder)

        subdirs = [x[0] for x in os.walk(self.data_dir)]
        potential_folders = sorted(list(filter(lambda d: most_recent_folder in d, subdirs)))
        parent_dirs = []
        for folder in potential_folders:
            path = os.path.normpath(folder)
            split_folder = path.split(os.sep)
            if most_recent_folder in split_folder[-1]:
                parent_dirs.append(folder)
        parent_dir = sorted(parent_dirs, reverse=True)[0]
        return Ok(parent_dir)

    @abc.abstractmethod
    def retrieve_recent_data_files(self):
        pass

    @abc.abstractmethod
    def get_data(self) -> Union[list[AgilentChannelChromatogramData], AgilentChannelChromatogramData]:
        pass

    def get_uv_spectrum(self, path: str):
        data_uv = rb.agilent.chemstation.parse_file(os.path.join(path, "DAD1.UV"))
        zipped_data = zip(data_uv.ylabels, data_uv.data)
        self.uv = {str(w_a[0]): ChromData(x=data_uv.xlabels, y=w_a[1]) for w_a in zipped_data}

    def get_spectrum(self, data_path: str, read_uv: bool = False):
        """
        Load chromatogram for any channel in spectra dictionary.
        """
        if read_uv:
            self.get_uv_spectrum(data_path)

        for channel, spec in self.spectra.items():
            try:
                spec.load_spectrum(data_path=data_path, channel=channel)
            except FileNotFoundError:
                self.spectra[channel] = AgilentHPLCChromatogram(self.data_dir)
                print(f"No data at channel: {channel}")
