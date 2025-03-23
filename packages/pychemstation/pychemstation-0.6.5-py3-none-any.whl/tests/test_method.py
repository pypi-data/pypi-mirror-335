import os
import unittest

from pychemstation.control import HPLCController
from tests.constants import *


class TestMethod(unittest.TestCase):
    def setUp(self):
        path_constants = room(254)
        for path in path_constants:
            if not os.path.exists(path):
                self.fail(
                    f"{path} does not exist on your system. If you would like to run tests, please change this path.")

        self.hplc_controller = HPLCController(comm_dir=path_constants[0],
                                              method_dir=path_constants[1],
                                              data_dir=path_constants[2],
                                              sequence_dir=path_constants[3])

    def test_load_method_from_disk(self):
        self.hplc_controller.switch_method(DEFAULT_METHOD)
        try:
            gp_mtd = self.hplc_controller.method_controller.load_from_disk(DEFAULT_METHOD)
            self.assertTrue(gp_mtd.first_row.organic_modifier == 5)
        except Exception as e:
            self.fail(f"Should have not failed, {e}")

    def test_edit_method(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
        new_method = MethodDetails(name=DEFAULT_METHOD,
                                   timetable=[TimeTableEntry(start_time=1,
                                                             organic_modifer=20,
                                                             flow=0.65),
                                              TimeTableEntry(start_time=2,
                                                             organic_modifer=30,
                                                             flow=0.65),
                                              TimeTableEntry(start_time=2.5,
                                                             organic_modifer=60,
                                                             flow=0.65),
                                              TimeTableEntry(start_time=3,
                                                             organic_modifer=80,
                                                             flow=0.65),
                                              TimeTableEntry(start_time=3.5,
                                                             organic_modifer=100,
                                                             flow=0.65)],
                                   stop_time=4,
                                   post_time=1,
                                   params=HPLCMethodParams(organic_modifier=5, flow=0.65))
        try:
            self.hplc_controller.edit_method(new_method)
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_load_method(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
        new_method = gen_rand_method()
        try:
            self.hplc_controller.edit_method(new_method)
            loaded_method = self.hplc_controller.load_method()
            self.assertEqual(new_method.params.organic_modifier,
                             loaded_method.params.organic_modifier)
            self.assertEqual(new_method.timetable[0].organic_modifer,
                             loaded_method.timetable[0].organic_modifer)
            self.assertEqual(round(new_method.params.flow, 2),
                             round(loaded_method.params.flow, 2))
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

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


if __name__ == '__main__':
    unittest.main()
