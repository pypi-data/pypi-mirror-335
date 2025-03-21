# Agilent HPLC Macro Control

![PyPI - Downloads](https://img.shields.io/pypi/dm/pychemstation)

[![PyPI Latest Release](https://img.shields.io/pypi/v/pychemstation.svg)](https://pypi.org/project/pychemstation/)

Unofficial Python package to control Agilent Chemstation; we are not affiliated with Agilent.
Check out the [docs](https://hein-analytical-control-5e6e85.gitlab.io/) for usage instructions. This project is under
active development, and breaking changes may occur at any moment.

## Getting started

Before running this library, these are the steps you need to complete.

### Add python package

```bash
pip install pychemstation
```

### Add required MACRO script

1. Open ChemStation
2. Run this in the ChemStation command line: ``Print _AutoPath$``. Go to this path in your file navigator, as this is
   where you will put your
   MACRO file(s).
3. Download the [
   `hplc_talk.mac`](https://gitlab.com/heingroup/device-api/pychemstation/-/blob/main/tests/hplc_talk.mac).
    - On line 69, change the path name up to `\cmd` and `\reply`. For instance, you should have:
      `MonitorFile "[my path]\cmd", "[my path]\reply"`
    - and then add this file to the folder from the previous step.
4. To have these MACRO files be read by ChemStation, you must either:
    - Open ChemStation and run:

```MACRO
macro hplc_talk.mac
HPLCTalk_Run
```

- OR add the above lines to a MACRO file named: `user.mac`, and then put `user.mac` in the same folder from step 3.
    - ChemStation will automatically load these MACRO files for you. However, sometimes this does not work, and if it
      does not, you will have to run the lines in the `user.mac` manually.

## Example Usage

```python
from pychemstation.control import HPLCController
import pandas as pd

# these paths will be unique to your Chemstation setup
DEFAULT_COMMAND_PATH = "C:\\Users\\User\\Desktop\\Lucy\\"
DEFAULT_METHOD = "GENERAL-POROSHELL"
DEFAULT_METHOD_DIR = "C:\\ChemStation\\1\\Methods\\"
DATA_DIR = "C:\\Users\\Public\\Documents\\ChemStation\\2\\Data"
SEQUENCE_DIR = "C:\\USERS\\PUBLIC\\DOCUMENTS\\CHEMSTATION\\2\\Sequence"

hplc_controller = HPLCController(data_dir=DATA_DIR,
                                 comm_dir=DEFAULT_COMMAND_PATH,
                                 sequence_dir=SEQUENCE_DIR,
                                 method_dir=DEFAULT_METHOD_DIR)

hplc_controller.preprun()
hplc_controller.switch_method(method_name=DEFAULT_METHOD)
hplc_controller.run_method(experiment_name="Run 10")
chrom = hplc_controller.get_last_run_method_data()

# afterwards, save, analyze or plot the data!
values = {"x": chrom.A.x, "y": chrom.A.y}
chromatogram_data = pd.DataFrame.from_dict(values)
chromatogram_data.to_csv("Run 10.csv", index=False) 
```

## Adding your own MACROs

If you wish to add your own MACRO functions, then all you need to do is write you MACRO (using Agilent's) MACRO guide,
put the file in the `user.mac` file and then list the function you want to use.

## Developing

If you would like to contribute to this project, check out
our [GitLab](https://gitlab.com/heingroup/device-api/pychemstation)!

## Authors and Acknowledgements

Lucy Hao, Maria Politi

- Adapted from [**AnalyticalLabware**](https://github.com/croningp/analyticallabware), created by members in the Cronin
  Group. Copyright © Cronin Group, used under the [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) license.
- Adapted from the [MACROS](https://github.com/Bourne-Group/HPLCMethodOptimisationGUI)
  used in [**Operator-free HPLC automated method development guided by Bayesian optimization**](https://pubs.rsc.org/en/content/articlelanding/2024/dd/d4dd00062e),
  created by members in the Bourne Group.  Copyright © Bourne Group, used under the [MIT](https://opensource.org/license/mit) license.