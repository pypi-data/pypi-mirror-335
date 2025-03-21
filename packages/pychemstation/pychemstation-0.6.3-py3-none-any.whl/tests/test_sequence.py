import os
import unittest

from pychemstation.control import HPLCController
from tests.constants import *


class TestSequence(unittest.TestCase):
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

    def test_switch(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
        except Exception as e:
            self.fail(f"Should have not expected: {e}")

    def test_edit_row(self):
        self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
        try:
            self.hplc_controller.edit_sequence_row(SequenceEntry(
                vial_location=TenVialColumn.TEN,
                method=DEFAULT_METHOD,
                num_inj=3,
                inj_vol=4,
                sample_name="Blank",
                sample_type=SampleType.BLANK,
                inj_source=InjectionSource.HIP_ALS
            ), 1)
        except Exception:
            self.fail("Should have not failed")

    def test_edit_entire_table(self):
        self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
        try:
            seq_table = SequenceTable(
                name=DEFAULT_SEQUENCE,
                rows=[
                    SequenceEntry(
                        vial_location=TenVialColumn.ONE,
                        method=DEFAULT_METHOD,
                        num_inj=3,
                        inj_vol=4,
                        sample_name="Sampel1",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS
                    ),
                    SequenceEntry(
                        vial_location=TenVialColumn.TWO,
                        method=DEFAULT_METHOD,
                        num_inj=3,
                        inj_vol=4,
                        sample_name="Sampel2",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS
                    ),
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
