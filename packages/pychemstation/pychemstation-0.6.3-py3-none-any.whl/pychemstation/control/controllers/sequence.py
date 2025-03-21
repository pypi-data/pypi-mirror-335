import os
import time
from typing import Optional

from ...control.controllers.comm import CommunicationController
from ...control.controllers.table_controller import TableController
from ...utils.chromatogram import SEQUENCE_TIME_FORMAT, AgilentChannelChromatogramData
from ...utils.macro import Command
from ...utils.sequence_types import SequenceTable, SequenceEntry, SequenceDataFiles, InjectionSource, SampleType
from ...utils.table_types import RegisterFlag, Table
from ...utils.tray_types import TenVialColumn


class SequenceController(TableController):
    """
    Class containing sequence related logic
    """

    def __init__(self, controller: CommunicationController, src: str, data_dir: str, table: Table, method_dir: str):
        self.method_dir = method_dir
        super().__init__(controller, src, data_dir, table)

    def load(self) -> SequenceTable:
        rows = self.get_num_rows()
        self.send(Command.GET_SEQUENCE_CMD)
        seq_name = self.receive()

        if rows.is_ok() and seq_name.is_ok():
            self.table_state = SequenceTable(
                name=seq_name.ok_value.string_response.partition(".S")[0],
                rows=[self.get_row(r + 1) for r in range(int(rows.ok_value.num_response))])
            return self.table_state
        raise RuntimeError(rows.err_value)

    def get_row(self, row: int) -> SequenceEntry:
        sample_name = self.get_text(row, RegisterFlag.NAME)
        vial_location = int(self.get_num(row, RegisterFlag.VIAL_LOCATION))
        method = self.get_text(row, RegisterFlag.METHOD)
        num_inj = int(self.get_num(row, RegisterFlag.NUM_INJ))
        inj_vol = int(self.get_text(row, RegisterFlag.INJ_VOL))
        inj_source = InjectionSource(self.get_text(row, RegisterFlag.INJ_SOR))
        sample_type = SampleType(self.get_num(row, RegisterFlag.SAMPLE_TYPE))
        return SequenceEntry(sample_name=sample_name,
                             vial_location=vial_location,
                             method=None if len(method) == 0 else method,
                             num_inj=num_inj,
                             inj_vol=inj_vol,
                             inj_source=inj_source,
                             sample_type=sample_type)

    def check(self) -> str:
        time.sleep(2)
        self.send(Command.GET_SEQUENCE_CMD)
        time.sleep(2)
        res = self.receive()
        if res.is_ok():
            return res.ok_value.string_response
        return "ERROR"

    def switch(self, seq_name: str):
        """
        Switch to the specified sequence. The sequence name does not need the '.S' extension.

        :param seq_name: The name of the sequence file
        """
        self.send(f'_SeqFile$ = "{seq_name}.S"')
        self.send(f'_SeqPath$ = "{self.src}"')
        self.send(Command.SWITCH_SEQUENCE_CMD)
        time.sleep(2)
        self.send(Command.GET_SEQUENCE_CMD)
        time.sleep(2)
        parsed_response = self.receive().value.string_response

        assert parsed_response == f"{seq_name}.S", "Switching sequence failed."
        self.table_state = None

    def edit(self, sequence_table: SequenceTable):
        """
        Updates the currently loaded sequence table with the provided table. This method will delete the existing sequence table and remake it.
        If you would only like to edit a single row of a sequence table, use `edit_sequence_table_row` instead.

        :param sequence_table:
        """
        self.table_state = sequence_table
        rows = self.get_num_rows()
        if rows.is_ok():
            existing_row_num = rows.value.num_response
            wanted_row_num = len(sequence_table.rows)
            while existing_row_num != wanted_row_num:
                if wanted_row_num > existing_row_num:
                    self.add_row()
                elif wanted_row_num < existing_row_num:
                    self.delete_row(int(existing_row_num))
                self.send(Command.SAVE_SEQUENCE_CMD)
                existing_row_num = self.get_num_rows().ok_value.num_response
            self.send(Command.SWITCH_SEQUENCE_CMD)

            for i, row in enumerate(sequence_table.rows):
                self.edit_row(row=row, row_num=i + 1)
                self.sleep(1)
            self.send(Command.SAVE_SEQUENCE_CMD)
            self.send(Command.SWITCH_SEQUENCE_CMD)

    def edit_row(self, row: SequenceEntry, row_num: int):
        """
        Edits a row in the sequence table. If a row does NOT exist, a new one will be created.

        :param row: sequence row entry with updated information
        :param row_num: the row to edit, based on 1-based indexing
        """
        num_rows = self.get_num_rows()
        if num_rows.is_ok():
            while num_rows.ok_value.num_response < row_num:
                self.add_row()
                self.send(Command.SAVE_SEQUENCE_CMD)
                num_rows = self.get_num_rows()

        if row.vial_location:
            loc = row.vial_location
            if isinstance(row.vial_location, TenVialColumn):
                loc = row.vial_location.value
            self.edit_row_num(row=row_num, col_name=RegisterFlag.VIAL_LOCATION, val=loc)

        if row.method:
            possible_path = os.path.join(self.method_dir, row.method) + ".M\\"
            method = row.method
            if os.path.exists(possible_path):
                method = os.path.join(self.method_dir, row.method)
            self.edit_row_text(row=row_num, col_name=RegisterFlag.METHOD, val=method)

        if row.num_inj:
            self.edit_row_num(row=row_num, col_name=RegisterFlag.NUM_INJ, val=row.num_inj)

        if row.inj_vol:
            self.edit_row_text(row=row_num, col_name=RegisterFlag.INJ_VOL, val=row.inj_vol)

        if row.inj_source:
            self.edit_row_text(row=row_num, col_name=RegisterFlag.INJ_SOR, val=row.inj_source.value)

        if row.sample_name:
            self.edit_row_text(row=row_num, col_name=RegisterFlag.NAME, val=row.sample_name)
            self.edit_row_text(row=row_num, col_name=RegisterFlag.DATA_FILE, val=row.sample_name)

        if row.sample_type:
            self.edit_row_num(row=row_num, col_name=RegisterFlag.SAMPLE_TYPE, val=row.sample_type.value)

        self.send(Command.SAVE_SEQUENCE_CMD)

    def run(self, stall_while_running: bool = True):
        """
        Starts the currently loaded sequence, storing data
        under the <data_dir>/<sequence table name> folder.
        Device must be ready.
        """
        if not self.table_state:
            self.table_state = self.load()

        timestamp = time.strftime(SEQUENCE_TIME_FORMAT)
        self.send(Command.RUN_SEQUENCE_CMD.value)

        if self.check_hplc_is_running():
            folder_name = f"{self.table_state.name} {timestamp}"
            self.data_files.append(SequenceDataFiles(dir=folder_name,
                                                     sequence_name=self.table_state.name))

            if stall_while_running:
                run_completed = self.check_hplc_done_running(sequence=self.table_state)
                if run_completed.is_ok():
                    self.data_files[-1].dir = run_completed.value
                else:
                    raise RuntimeError("Run error has occurred.")
            else:
                self.data_files[-1].dir = self.fuzzy_match_most_recent_folder(folder_name).ok_value

    def retrieve_recent_data_files(self) -> str:
        sequence_data_files: SequenceDataFiles = self.data_files[-1]
        return sequence_data_files.dir

    def get_data(self, custom_path: Optional[str] = None) -> list[AgilentChannelChromatogramData]:
        parent_dir = self.data_files[-1].dir if not custom_path else custom_path
        subdirs = [x[0] for x in os.walk(self.data_dir)]
        potential_folders = sorted(list(filter(lambda d: parent_dir in d, subdirs)))
        self.data_files[-1].child_dirs = [f for f in potential_folders if
                                          parent_dir in f and ".M" not in f and ".D" in f]

        spectra: list[AgilentChannelChromatogramData] = []
        for row in self.data_files[-1].child_dirs:
            self.get_spectrum(row)
            spectra.append(AgilentChannelChromatogramData(**self.spectra))
        return spectra
