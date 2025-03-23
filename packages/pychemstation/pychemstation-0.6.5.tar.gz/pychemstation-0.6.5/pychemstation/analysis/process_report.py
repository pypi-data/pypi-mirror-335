import os
import re
from dataclasses import dataclass
from typing import List, AnyStr, Dict

import pandas as pd
from aghplctools.ingestion.text import _no_peaks_re, _area_report_re, _header_block_re, _signal_info_re, \
    _signal_table_re, chunk_string
from result import Result, Err, Ok

from pychemstation.utils.tray_types import Tray, FiftyFourVialPlate


@dataclass
class AgilentPeak:
    peak_number: int
    retention_time: float
    peak_type: str
    width: float
    area: float
    height: float
    height_percent: float


@dataclass
class AgilentReport:
    vial_location: Tray
    signals: Dict[AnyStr, List[AgilentPeak]]
    solvents: Dict[AnyStr, AnyStr]


_column_re_dictionary = {  # regex matches for column and unit combinations
    'Peak': {  # peak index
        '#': '[ ]+(?P<Peak>[\d]+)',  # number
    },
    'RetTime': {  # retention time
        '[min]': '(?P<RetTime>[\d]+.[\d]+)',  # minutes
    },
    'Type': {  # peak type
        '': '(?P<Type>[A-Z]{1,3}(?: [A-Z]{1,2})*)',  # todo this is different from <4.8.8 aghplc tools
    },
    'Width': {  # peak width
        '[min]': '(?P<Width>[\d]+.[\d]+[e+-]*[\d]+)',
    },
    'Area': {  # peak area
        '[mAU*s]': '(?P<Area>[\d]+.[\d]+[e+-]*[\d]+)',  # area units
        '%': '(?P<percent>[\d]+.[\d]+[e+-]*[\d]+)',  # percent
    },
    'Height': {  # peak height
        '[mAU]': '(?P<Height>[\d]+.[\d]+[e+-]*[\d]+)',
    },
    'Name': {
        '': '(?P<Name>[^\s]+(?:\s[^\s]+)*)',  # peak name
    },
}


def build_peak_regex(signal_table: str) -> re.Pattern[AnyStr]:
    """
    Builds a peak regex from a signal table

    :param signal_table: block of lines associated with an area table
    :return: peak line regex object (<=3.6 _sre.SRE_PATTERN, >=3.7 re.Pattern)
    """
    split_table = signal_table.split('\n')
    if len(split_table) <= 4:  # catch peak table with no values
        return None
    # todo verify that these indicies are always true
    column_line = split_table[2]  # table column line
    unit_line = split_table[3]  # column unit line
    length_line = [len(val) + 1 for val in split_table[4].split('|')]  # length line

    # iterate over header values and units to build peak table regex
    peak_re_string = []
    for header, unit in zip(
            chunk_string(column_line, length_line),
            chunk_string(unit_line, length_line)
    ):
        if header == '':  # todo create a better catch for an undefined header
            continue
        try:
            peak_re_string.append(
                _column_re_dictionary[header][unit]  # append the appropriate regex
            )
        except KeyError:  # catch for undefined regexes (need to be built)
            raise KeyError(f'The header/unit combination "{header}" "{unit}" is not defined in the peak regex '
                           f'dictionary. Let Lars know.')
    return re.compile(
        '[ ]+'.join(peak_re_string)  # constructed string delimited by 1 or more spaces
        + '[\s]*'  # and any remaining white space
    )


# todo should be able to use the parse_area_report method of aghplctools v4.8.8

def parse_area_report(report_text: str) -> dict:
    """
    Interprets report text and parses the area report section, converting it to dictionary.

    :param report_text: plain text version of the report.
    :raises ValueError: if there are no peaks defined in the report text file
    :return: dictionary of signals in the form
        dict[wavelength][retention time (float)][Width/Area/Height/etc.]
    """
    if re.search(_no_peaks_re, report_text):  # There are no peaks in Report.txt
        raise ValueError(f'No peaks found in Report.txt')
    blocks = _header_block_re.split(report_text)
    signals = {}  # output dictionary
    for ind, block in enumerate(blocks):
        # area report block
        if _area_report_re.match(block):  # match area report block
            # break into signal blocks
            signal_blocks = _signal_table_re.split(blocks[ind + 1])
            # iterate over signal blocks
            for table in signal_blocks:
                si = _signal_info_re.match(table)
                if si is not None:
                    # some error state (e.g. 'not found')
                    if si.group('error') != '':
                        continue
                    wavelength = float(si.group('wavelength'))
                    if wavelength in signals:
                        # placeholder error raise just in case (this probably won't happen)
                        raise KeyError(
                            f'The wavelength {float(si.group("wavelength"))} is already in the signals dictionary')
                    signals[wavelength] = {}
                    # build peak regex
                    peak_re = build_peak_regex(table)
                    if peak_re is None:  # if there are no columns (empty table), continue
                        continue
                    for line in table.split('\n'):
                        peak = peak_re.match(line)
                        if peak is not None:
                            signals[wavelength][float(peak.group('RetTime'))] = {}
                            current = signals[wavelength][float(peak.group('RetTime'))]
                            for key in _column_re_dictionary:
                                if key in peak.re.groupindex:
                                    try:  # try float conversion, otherwise continue
                                        value = float(peak.group(key))
                                    except ValueError:
                                        value = peak.group(key)
                                    current[key] = value
                                else:  # ensures defined
                                    current[key] = None
    return signals


def process_export_report(file_path, target_wavelengths=None, min_retention_time=0, max_retention_time=999):
    # # Pull signals from the file
    # from aghplctools.ingestion.text import pull_hplc_area_from_txt
    # signals = pull_hplc_area_from_txt(file_path)

    with open(file_path, 'r', encoding='utf-16') as openfile:
        text = openfile.read()

    try:
        signals = parse_area_report(text)
    except ValueError as e:
        # value error thrown if there are no peaks found in the report
        print(e)
        return [], [], []

    # filter wavelengths by the ones to keep
    if target_wavelengths is not None:
        signals = {key: signals[key] for key in target_wavelengths if key in signals}

    wavelengths = []
    retention_times = []
    areas = []

    for wavelength, wavelength_dict in signals.items():
        for ret_time, ret_time_dict in wavelength_dict.items():
            if min_retention_time <= ret_time <= max_retention_time:
                wavelengths.append(wavelength)
                retention_times.append(ret_time)
                areas.append(ret_time_dict['Area'])

    return wavelengths, retention_times, areas


def process_folder(folder_path, target_wavelengths=None, min_retention_time=0, max_retention_time=999):
    # folder path is the path to the overall folder, and inside there should be subfolders for each LC sample
    # each subfolder should have a Report.TXT file
    # sample_names = []
    wavelengths = []
    retention_times = []
    peak_areas = []

    # Get a list of all items (files and directories) in the folder
    items = [os.path.join(folder_path, item) for item in os.listdir(folder_path)]

    # Filter only directories from the list
    # folders = [item for item in items if os.path.isdir(item)]

    # # Sort the folders by creation date
    # sorted_folders = sorted(folders, key=lambda f: os.stat(f).st_ctime)

    for filename in items:
        if filename.endswith('Report.TXT'):
            # file_path = os.path.join(subfolder, filename)
            file_wavelengths, file_retention_times, file_peak_areas = process_export_report(filename,
                                                                                            target_wavelengths,
                                                                                            min_retention_time,
                                                                                            max_retention_time)
            wavelengths.extend(file_wavelengths)
            retention_times.extend(file_retention_times)
            peak_areas.extend(file_peak_areas)

    results_df = pd.DataFrame({'Wavelengths': wavelengths, 'Retention Times': retention_times, 'Areas': peak_areas})

    # Save the results to a CSV file
    # results_csv_path = os.path.join(folder_path, 'all_sample_data.csv')  # Specify the desired file path
    # results_df.to_csv(results_csv_path, index=False)
    # print(f"Results saved to {results_csv_path}")
    return results_df


def process_csv_report(folder_path: str) -> Result[AgilentReport, AnyStr]:
    labels = os.path.join(folder_path, f'REPORT00.CSV')
    if os.path.exists(labels):
        df_labels: Dict[int, Dict[int: AnyStr]] = pd.read_csv(labels, encoding="utf-16", header=None).to_dict()
        vial_location = []
        signals = {}
        solvents = {}
        for pos, val in df_labels[0].items():
            if val == "Location":
                vial_location = df_labels[1][pos]
            elif "Solvent" in val:
                if val not in solvents.keys():
                    solvents[val] = df_labels[2][pos]
            elif val == "Number of Signals":
                num_signals = int(df_labels[1][pos])
                for s in range(1, num_signals + 1):
                    peaks = process_peaks(os.path.join(folder_path, f'REPORT0{s}.CSV'))
                    if peaks.is_ok():
                        wavelength = df_labels[1][pos + s].partition(",4 Ref=off")[0][-3:]
                        signals[wavelength] = peaks.ok_value
                break

        return Ok(AgilentReport(
            signals=signals,
            vial_location=FiftyFourVialPlate.from_int(vial_location),
            solvents=solvents
        ))

    return Err("No report found")


def process_peaks(folder_path: str) -> Result[List[AgilentPeak], AnyStr]:
    try:
        df = pd.read_csv(folder_path, encoding="utf-16", header=None)
        return Ok(df.apply(lambda row: AgilentPeak(*row), axis=1))
    except Exception:
        return Err("Trouble reading report")
