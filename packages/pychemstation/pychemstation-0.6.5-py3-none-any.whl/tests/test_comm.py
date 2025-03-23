import os

import unittest

from pychemstation.control import HPLCController
from pychemstation.utils.macro import *
from tests.constants import *


class TestComm(unittest.TestCase):

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

    def test_status_check_standby(self):
        self.hplc_controller.standby()
        self.assertTrue(self.hplc_controller.status() in [HPLCAvailStatus.STANDBY, HPLCRunningStatus.NOTREADY])

    def test_status_check_preprun(self):
        self.hplc_controller.preprun()
        self.assertTrue(self.hplc_controller.status() in [HPLCAvailStatus.PRERUN, HPLCAvailStatus.STANDBY,
                                                          HPLCRunningStatus.NOTREADY])

    def test_send_command(self):
        try:
            self.hplc_controller.send(Command.GET_METHOD_CMD)
        except Exception as e:
            self.fail(f"Should not throw error: {e}")

    def test_send_str(self):
        try:
            self.hplc_controller.send("Local TestNum")
            self.hplc_controller.send("TestNum = 0")
            self.hplc_controller.send("Print TestNum")
            self.hplc_controller.send("response_num = TestNum")
            self.hplc_controller.send("Print response_num")
        except Exception as e:
            self.fail(f"Should not throw error: {e}")

    def test_get_num(self):
        try:
            self.hplc_controller.send("response_num = 10")
            res = self.hplc_controller.receive().num_response
            self.assertEqual(res, 10)
        except Exception as e:
            self.fail(f"Should not throw error: {e}")

    def test_get_response(self):
        try:
            self.hplc_controller.switch_method(method_name=DEFAULT_METHOD)
            self.hplc_controller.send(Command.GET_METHOD_CMD)
            res = self.hplc_controller.receive()
            self.assertTrue(DEFAULT_METHOD in res.string_response)
        except Exception as e:
            self.fail(f"Should not throw error: {e}")

