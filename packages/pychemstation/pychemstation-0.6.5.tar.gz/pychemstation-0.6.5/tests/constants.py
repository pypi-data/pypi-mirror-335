import os
import random

from pychemstation.control import HPLCController
from pychemstation.utils.macro import Command
from pychemstation.utils.method_types import *
from pychemstation.utils.sequence_types import *

DEFAULT_METHOD = "GENERAL-POROSHELL-OPT"
DEFAULT_SEQUENCE = "hplc_testing"

# CONSTANTS: paths only work in Hein group HPLC machine in room 242
DEFAULT_COMMAND_PATH = "C:\\Users\\User\\Desktop\\Lucy\\"
DEFAULT_METHOD_DIR = "C:\\ChemStation\\1\\Methods\\"
DATA_DIR = "C:\\Users\\Public\\Documents\\ChemStation\\3\\Data"
SEQUENCE_DIR = "C:\\USERS\\PUBLIC\\DOCUMENTS\\CHEMSTATION\\3\\Sequence"

HEIN_LAB_CONSTANTS = [DEFAULT_COMMAND_PATH,
                      DEFAULT_METHOD_DIR,
                      DATA_DIR,
                      SEQUENCE_DIR]

# these CONSTANTS work in rm 254
DEFAULT_COMMAND_PATH_254 = "D:\\\git_repositories\\\hplc_comm\\"
DEFAULT_METHOD_DIR_254 = "D:\\Chemstation\\1\\Methods\\"
DATA_DIR_254 = "D:\\Chemstation\\1\\Data\\LC BO\\"
SEQUENCE_DIR_254 = "C:\\1\\Sequence\\"

HEIN_LAB_CONSTANTS_254 = [DEFAULT_COMMAND_PATH_254,
                          DEFAULT_METHOD_DIR_254,
                          DATA_DIR_254,
                          SEQUENCE_DIR_254]


def room(num: int):
    if num == 242:
        return HEIN_LAB_CONSTANTS
    elif num == 254:
        return HEIN_LAB_CONSTANTS_254


def gen_rand_method():
    org_modifier = int(random.random() * 10)
    max_run_time = int(random.random() * 10)
    post_run_time = int(random.random() * 10)
    flow = float(random.random() * 10) / 10
    flow_1 = float(random.random() * 10) / 10
    flow_2 = float(random.random() * 10) / 10
    return MethodDetails(name=DEFAULT_METHOD,
                         timetable=[TimeTableEntry(start_time=0.10,
                                                   organic_modifer=org_modifier,
                                                   flow=flow_1),
                                    TimeTableEntry(start_time=1,
                                                   organic_modifer=100 - int(random.random() * 10),
                                                   flow=flow_2)],
                         stop_time=max_run_time,
                         post_time=post_run_time,
                         params=HPLCMethodParams(organic_modifier=org_modifier, flow=flow))


seq_entry = SequenceEntry(
    vial_location=TenVialColumn.ONE,
    method=DEFAULT_METHOD,
    num_inj=int(random.random() * 10),
    inj_vol=int(random.random() * 10),
    sample_name="Test",
    sample_type=SampleType(int(random.random() * 3)),
)


def set_up_utils(num: int) -> HPLCController:
    path_constants = room(num)
    for path in path_constants:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{path} does not exist on your system. If you would like to run tests, please change this path.")

    controller = HPLCController(comm_dir=path_constants[0],
                                method_dir=path_constants[1],
                                data_dir=path_constants[2],
                                sequence_dir=path_constants[3])
    controller.send(Command.SAVE_METHOD_CMD.value.format(commit_msg="method saved by pychemstation"))
    controller.send(Command.SAVE_SEQUENCE_CMD)
    return controller
