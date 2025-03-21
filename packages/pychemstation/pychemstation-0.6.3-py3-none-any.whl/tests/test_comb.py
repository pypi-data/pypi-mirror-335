import os

import unittest

from pychemstation.control import HPLCController
from tests.constants import *

run_too = True


class TestCombinations(unittest.TestCase):
    def setUp(self):
        path_constants = room(242)
        for path in path_constants:
            if not os.path.exists(path):
                self.fail(
                    f"{path} does not exist on your system. If you would like to run tests, please change this path.")

        self.hplc_controller = HPLCController(comm_dir=path_constants[0],
                                              method_dir=path_constants[1],
                                              data_dir=path_constants[2],
                                              sequence_dir=path_constants[3])

    def test_run_method_after_update(self):
        try:
            self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
            rand_method = MethodDetails(
                params=HPLCMethodParams(organic_modifier=5,
                                        flow=0.65),
                timetable=[TimeTableEntry(start_time=3.5,
                                          organic_modifer=100,
                                          flow=0.65)],
                name=DEFAULT_METHOD,
                stop_time=10,
                post_time=9)
            self.hplc_controller.edit_method(rand_method, save=True)
            if run_too:
                self.hplc_controller.run_method(experiment_name="changed_method")
                chrom = self.hplc_controller.get_last_run_method_data()
                self.assertEqual(len(chrom.__dict__), 8)
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_run_after_table_edit(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            seq_table = self.hplc_controller.load_sequence()
            seq_table.rows.append(SequenceEntry(
                vial_location=TenVialColumn.ONE,
                method=DEFAULT_METHOD,
                num_inj=3,
                inj_vol=4,
                sample_name="Sampel1",
                sample_type=SampleType.SAMPLE,
            ))
            seq_table.rows[0] = SequenceEntry(
                vial_location=TenVialColumn.ONE,
                method=DEFAULT_METHOD,
                num_inj=3,
                inj_vol=4,
                sample_name="Sampel2",
                sample_type=SampleType.SAMPLE)
            self.hplc_controller.edit_sequence(seq_table)
            if run_too:
                self.hplc_controller.run_sequence()
                chrom = self.hplc_controller.get_last_run_sequence_data()
                self.assertTrue(len(chrom) == 2)
        except Exception as e:
            self.fail("Failed")

    def test_run_after_existing_row_edit(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            seq_table = self.hplc_controller.load_sequence()
            self.hplc_controller.edit_sequence_row(seq_entry, 1)
            if run_too:
                self.hplc_controller.run_sequence()
                chrom = self.hplc_controller.get_last_run_sequence_data()
                self.assertTrue(len(chrom) == 2)
        except Exception:
            self.fail("Failed")

    def test_update_method_update_seq_table_run(self):
        try:
            self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
            rand_method = MethodDetails(
                name=DEFAULT_METHOD,
                params=HPLCMethodParams(
                    organic_modifier=5,
                    flow=0.65),
                timetable=[TimeTableEntry(
                    start_time=0.50,
                    organic_modifer=99,
                    flow=0.34)],
                stop_time=10,
                post_time=5)
            self.hplc_controller.edit_method(rand_method, save=True)

            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            seq_table = SequenceTable(
                name=DEFAULT_SEQUENCE,
                rows=[SequenceEntry(
                    vial_location=8320,
                    sample_name="WM-01-001_Cr-Org",
                    method=DEFAULT_METHOD,
                    inj_source=InjectionSource.HIP_ALS,
                    inj_vol=2,
                    num_inj=1,
                    sample_type=SampleType.SAMPLE
                ), SequenceEntry(
                    vial_location=8448,
                    sample_name="WM-01-001_Cr-Aq",
                    method=DEFAULT_METHOD,
                    inj_source=InjectionSource.HIP_ALS,
                    inj_vol=2,
                    num_inj=1,
                    sample_type=SampleType.SAMPLE)])

            self.hplc_controller.edit_sequence(seq_table)
            if run_too:
                self.hplc_controller.preprun()
                self.hplc_controller.run_sequence()
                chrom = self.hplc_controller.get_last_run_sequence_data()
                self.assertTrue(len(chrom) == 2)
        except Exception:
            self.fail("Failed")

    def test_run_sequence(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            self.hplc_controller.preprun()
            self.hplc_controller.run_sequence()
            chrom = self.hplc_controller.get_last_run_sequence_data()
            self.assertTrue(len(chrom) == 1)
        except Exception:
            self.fail("Failed")
