import unittest

from pychemstation.utils.macro import *
from pychemstation.utils.tray_types import *
from tests.constants import *


class TestStable(unittest.TestCase):

    def setUp(self):
        self.hplc_controller = set_up_utils(254)

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

    def test_load_method_from_disk(self):
        self.hplc_controller.switch_method(DEFAULT_METHOD)
        try:
            gp_mtd = self.hplc_controller.method_controller.load_from_disk(DEFAULT_METHOD)
            self.assertTrue(gp_mtd.params.organic_modifier == 5)
        except Exception as e:
            self.fail(f"Should have not failed, {e}")

    def test_edit_method(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
        new_method = MethodDetails(name=DEFAULT_METHOD + ".M",
                                   timetable=[TimeTableEntry(start_time=1.0,
                                                             organic_modifer=20.0,
                                                             flow=0.65),
                                              TimeTableEntry(start_time=2.0,
                                                             organic_modifer=30.0,
                                                             flow=0.65),
                                              TimeTableEntry(start_time=2.5,
                                                             organic_modifer=60.0,
                                                             flow=0.65),
                                              TimeTableEntry(start_time=3.0,
                                                             organic_modifer=80.0,
                                                             flow=0.65),
                                              TimeTableEntry(start_time=3.5,
                                                             organic_modifer=100.0,
                                                             flow=0.65)],
                                   stop_time=4.0,
                                   post_time=1.0,
                                   params=HPLCMethodParams(organic_modifier=5.0, flow=0.65))
        try:
            self.hplc_controller.edit_method(new_method)
            self.assertEqual(new_method, self.hplc_controller.load_method())
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

    def test_switch(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
        except Exception as e:
            self.fail(f"Should have not expected: {e}")

    def test_read(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            table = self.hplc_controller.load_sequence()
            self.assertTrue(table)
        except Exception as e:
            self.fail(f"Should have not expected: {e}")

    def test_edit_entire_table(self):
        self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
        seq_folder = self.hplc_controller.sequence_controller.src
        meth_path = os.path.join(seq_folder, DEFAULT_METHOD)
        try:
            seq_table = SequenceTable(
                name=DEFAULT_SEQUENCE,
                rows=[
                    SequenceEntry(
                        vial_location=TenVialColumn.ONE,
                        method=meth_path,
                        num_inj=3,
                        inj_vol=4,
                        sample_name="Sampel1",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS
                    ),
                    SequenceEntry(
                        vial_location=FiftyFourVialPlate(plate=Plate.ONE, letter=Letter.A, num=Num.ONE),
                        method=meth_path,
                        num_inj=3,
                        inj_vol=4,
                        sample_name="Sampel2",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS
                    ),
                    SequenceEntry(
                        vial_location=FiftyFourVialPlate(plate=Plate.ONE, letter=Letter.A, num=Num.TWO),
                        method=meth_path,
                        num_inj=3,
                        inj_vol=4,
                        sample_name="Sampel2",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS
                    ),
                    SequenceEntry(
                        vial_location=FiftyFourVialPlate(plate=Plate.ONE, letter=Letter.A, num=Num.THREE),
                        method=meth_path,
                        num_inj=3,
                        inj_vol=4,
                        sample_name="Sampel2",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS
                    )
                ]
            )
            self.hplc_controller.edit_sequence(seq_table)
            self.assertEqual(seq_table,
                             self.hplc_controller.load_sequence())
        except Exception:
            self.fail("Should have not occured")

    def test_edit_entire_table_less_rows(self):
        self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
        try:
            seq_table = SequenceTable(
                name=DEFAULT_SEQUENCE,
                rows=[
                    SequenceEntry(
                        vial_location=TenVialColumn.TEN,
                        method=DEFAULT_METHOD,
                        num_inj=3,
                        inj_vol=4,
                        sample_name="Sampel2",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS
                    ),
                    SequenceEntry(
                        vial_location=TenVialColumn.THREE,
                        method=DEFAULT_METHOD,
                        num_inj=3,
                        inj_vol=4,
                        sample_name="Sampel2",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS
                    )
                ]
            )
            self.hplc_controller.edit_sequence(seq_table)
        except Exception:
            self.fail("Should have not occured")

    def test_load(self):
        try:
            seq = self.hplc_controller.load_sequence()
            self.assertTrue(len(seq.rows) > 0)
        except Exception as e:
            self.fail(f"Should have not expected: {e}")

    def test_tray_nums(self):
        vial_locations = [
            FiftyFourVialPlate.from_str('P1-A7'),
            FiftyFourVialPlate.from_str('P1-B4'),
            FiftyFourVialPlate.from_str('P1-C2'),
            FiftyFourVialPlate.from_str('P1-D8'),
            FiftyFourVialPlate.from_str('P1-E3'),
            FiftyFourVialPlate.from_str('P1-F5'),
            # plate 2
            FiftyFourVialPlate.from_str('P2-A7'),
            FiftyFourVialPlate.from_str('P2-B2'),
            FiftyFourVialPlate.from_str('P2-C1'),
            FiftyFourVialPlate.from_str('P2-D8'),
            FiftyFourVialPlate.from_str('P2-E3'),
            FiftyFourVialPlate.from_str('P2-F6'),
        ]
        seq_table = SequenceTable(
            name=DEFAULT_SEQUENCE,
            rows=[
                SequenceEntry(
                    vial_location=v,
                    method=DEFAULT_METHOD,
                    num_inj=3,
                    inj_vol=4,
                    sample_name="Sampel2",
                    sample_type=SampleType.SAMPLE,
                    inj_source=InjectionSource.HIP_ALS
                ) for v in vial_locations
            ]
        )
        self.hplc_controller.edit_sequence(seq_table)
        loaded_table = self.hplc_controller.load_sequence()
        for i in range(len(vial_locations)):
            self.assertTrue(vial_locations[i].value()
                            == seq_table.rows[i].vial_location.value()
                            == loaded_table.rows[i].vial_location.value())

    def test_tray_nums_only(self):
        vial_locations = [
            # plate 2
            FiftyFourVialPlate.from_str('P2-A7'),
            FiftyFourVialPlate.from_str('P2-B2'),
            FiftyFourVialPlate.from_str('P2-C1'),
            FiftyFourVialPlate.from_str('P2-D8'),
            FiftyFourVialPlate.from_str('P2-E3'),
            FiftyFourVialPlate.from_str('P2-F6'),
            # plate 1
            FiftyFourVialPlate.from_str('P1-A7'),
            FiftyFourVialPlate.from_str('P1-B4'),
            FiftyFourVialPlate.from_str('P1-C2'),
            FiftyFourVialPlate.from_str('P1-D8'),
            FiftyFourVialPlate.from_str('P1-E3'),
            FiftyFourVialPlate.from_str('P1-F5'),
        ]

        for i in range(len(vial_locations)):
            self.assertEqual(vial_locations[i], FiftyFourVialPlate.from_int(vial_locations[i].value()))


if __name__ == '__main__':
    unittest.main()
