from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TableOperation(Enum):
    def __str__(self):
        return '%s' % self.value

    DELETE_TABLE = 'DelTab {register}, "{table_name}"'
    CREATE_TABLE = 'NewTab {register}, "{table_name}"'
    NEW_ROW = 'InsTabRow {register}, "{table_name}"'
    DELETE_ROW = 'DelTabRow {register}, "{table_name}", {row}'
    EDIT_ROW_VAL = 'SetTabVal "{register}", "{table_name}", {row}, "{col_name}", {val}'
    EDIT_ROW_TEXT = 'SetTabText "{register}", "{table_name}", {row}, "{col_name}", "{val}"'
    GET_ROW_VAL = 'TabVal("{register}", "{table_name}", {row}, "{col_name}")'
    GET_ROW_TEXT = 'TabText$("{register}", "{table_name}", {row}, "{col_name}")'
    GET_NUM_ROWS = 'Rows = TabHdrVal({register}, "{table_name}", "{col_name}")'
    GET_OBJ_HDR_VAL = 'ObjHdrVal("{register}", "{register_flag}")'
    GET_OBJ_HDR_TEXT = 'ObjHdrText$("{register}", "{register_flag}")'
    UPDATE_OBJ_HDR_VAL = 'SetObjHdrVal {register}, {register_flag}, {val}'
    UPDATE_OBJ_HDR_TEXT = 'SetObjHdrText {register}, {register_flag}, {val}'
    NEW_COL_TEXT = 'NewColText {register}, "{table_name}", "{col_name}", "{val}"'
    NEW_COL_VAL = 'NewColVal {register}, "{table_name}", "{col_name}", {val}'


class RegisterFlag(Enum):
    def __str__(self):
        return '%s' % self.value

    # for table
    NUM_ROWS = "NumberOfRows"

    # for Method
    SOLVENT_A_COMPOSITION = "PumpChannel_CompositionPercentage"
    SOLVENT_B_COMPOSITION = "PumpChannel2_CompositionPercentage"
    SOLVENT_C_COMPOSITION = "PumpChannel3_CompositionPercentage"
    SOLVENT_D_COMPOSITION = "PumpChannel4_CompositionPercentage"
    FLOW = "Flow"
    MAX_TIME = "StopTime_Time"
    POST_TIME = "PostTime_Time" #TODO: check
    COLUMN_OVEN_TEMP1 = "TemperatureControl_Temperature"
    COLUMN_OVEN_TEMP2 = "TemperatureControl2_Temperature"
    STOPTIME_MODE = "StopTime_Mode"
    POSTIME_MODE = "PostTime_Mode"
    TIME = "Time"
    TIMETABLE_SOLVENT_B_COMPOSITION = "SolventCompositionPumpChannel2_Percentage"
    TIMETABLE_FLOW = "FlowFlow"

    # for Method Timetable
    SOLVENT_COMPOSITION = "SolventComposition"
    PRESSURE = "Pressure"
    EXTERNAL_CONTACT = "ExternalContact"
    FUNCTION = "Function"


    # for Sequence
    VIAL_LOCATION = "Vial"
    NAME = "SampleName"
    METHOD = "Method"
    INJ_VOL = "InjVolume"
    INJ_SOR = "InjectionSource"
    NUM_INJ = "InjVial"
    SAMPLE_TYPE = "SampleType"
    DATA_FILE = "DataFileName"

    # for Injector Table
    ## Draw
    DRAW_SOURCE = "DrawSource"
    DRAW_VOLUME = "DrawVolume_Mode"
    DRAW_SPEED = "DrawSpeed_Mode"
    DRAW_OFFSET = "DrawOffset_Mode"
    # SetObjHdrVal RCWLS1Pretreatment[1], "DrawVolume_Value", 1
    DRAW_VOLUME_VALUE = "DrawVolume_Value"
    DRAW_LOCATION = "DrawLocation"
    DRAW_LOCATION_TRAY = "DrawLocationPlus_Tray"
    DRAW_LOCATION_UNIT = "DrawLocationPlus_Unit"
    DRAW_LOCATION_ROW = "DrawLocationPlus_Row"
    DRAW_LOCATION_COLUMN = "DrawLocationPlus_Column"
    ## Inject
    ## Wait
    ## Remote
    REMOTE = "RemoteLine"
    REMOTE_DUR = "RemoteDuration"



@dataclass
class Table:
    register: str
    name: str
