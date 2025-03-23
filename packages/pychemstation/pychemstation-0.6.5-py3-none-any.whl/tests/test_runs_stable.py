
import unittest

from pychemstation.utils.tray_types import FiftyFourVialPlate, Plate, Letter, Num
from tests.constants import *

run_too = True


class TestRunsStable(unittest.TestCase):
    def setUp(self):
        self.hplc_controller = set_up_utils(254)

    def test_run_method(self):
        try:
            self.hplc_controller.run_method(experiment_name="test_experiment")
            chrom = self.hplc_controller.get_last_run_method_data()
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_run_10_times(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
        rand_method = MethodDetails(
            name=DEFAULT_METHOD,
            params=HPLCMethodParams(
                organic_modifier=5,
                flow=0.65),
            timetable=[TimeTableEntry(
                start_time=0.50,
                organic_modifer=99,
                flow=0.65)],
            stop_time=1,
            post_time=0)
        self.hplc_controller.edit_method(rand_method, save=True)
        try:
            for _ in range(10):
                self.hplc_controller.run_method(experiment_name="limiting_testing")
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_update_method_update_seq_table_run(self):
        try:
            loc = FiftyFourVialPlate(plate=Plate.ONE, letter=Letter.F, num=Num.TWO)
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            seq_table = SequenceTable(
                name=DEFAULT_SEQUENCE,
                rows=[SequenceEntry(
                    vial_location=loc,
                    sample_name="run seq with new method",
                    method=DEFAULT_METHOD,
                    inj_source=InjectionSource.HIP_ALS,
                    inj_vol=0.5,
                    num_inj=1,
                    sample_type=SampleType.SAMPLE
                )])
            self.hplc_controller.edit_sequence(seq_table) # bug didnt delete all the rows, left an extra

            self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
            rand_method = MethodDetails(
                name=DEFAULT_METHOD,
                params=HPLCMethodParams(
                    organic_modifier=5,
                    flow=0.65),
                timetable=[TimeTableEntry(
                    start_time=random.randint(1, 3) + 0.50,
                    organic_modifer=100,
                    flow=0.65)],
                stop_time=random.randint(4, 6),
                post_time=1)
            self.hplc_controller.edit_method(rand_method, save=True)
            if run_too:
                self.hplc_controller.preprun()
                self.hplc_controller.run_sequence()
                chrom = self.hplc_controller.get_last_run_sequence_data()
                # report = process_csv_report(self.hplc_controller.sequence_controller.data_files[-1].child_dirs[-1])
                # self.assertEqual(loc, report.ok_value.vial_location)
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
