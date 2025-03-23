import os
import unittest

from pychemstation.control import HPLCController
from pychemstation.utils.tray_types import FiftyFourVialPlate, Letter, Plate, Num
from tests.constants import *

offline = True


class TestInj(unittest.TestCase):
    def setUp(self):
        path_constants = room(254)
        for path in path_constants:
            if not offline and not os.path.exists(path):
                self.fail(
                    f"{path} does not exist on your system. If you would like to run tests, please change this path.")

        self.hplc_controller = HPLCController(offline=offline,
                                              comm_dir=path_constants[0],
                                              method_dir=path_constants[1],
                                              data_dir=path_constants[2],
                                              sequence_dir=path_constants[3])
        if not offline:
            self.hplc_controller.switch_method(DEFAULT_METHOD)

    def test_load_inj(self):
        try:
            inj_table = self.hplc_controller.load_injector_program()
            self.assertTrue(len(inj_table.functions) == 2)
        except Exception as e:
            self.fail(f"Should have not failed, {e}")

    def test_plate_number(self):
        self.assertEqual(4096, FiftyFourVialPlate(plate=Plate.ONE, letter=Letter.A, num=Num.FOUR).value())


if __name__ == '__main__':
    unittest.main()
