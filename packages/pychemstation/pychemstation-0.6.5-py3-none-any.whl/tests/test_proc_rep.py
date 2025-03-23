import unittest

from result import Result

from pychemstation.analysis.process_report import process_csv_report


class TestReport(unittest.TestCase):

    def test_build_peak_regex(self):
        try:
            # TODO
            print('yes')
        except Exception as e:
            self.fail(f"Should have not failed, {e}")

    def test_parse_area_report(self):
        try:
            # TODO
            print('yes')
        except Exception as e:
            self.fail(f"Should have not failed, {e}")

    def test_process_export_report(self):
        try:
            import pandas as pd

            file_path = "/Users/lucyhao/Codes/pychemstation/tests/0_2025-03-15 19-14-35.D/Report00.CSV"
            df = pd.read_csv(file_path, encoding="utf-16")

            # Print the first column
            print(df)
        except Exception as e:
            self.fail(f"Should have not failed, {e}")

    def test_process_folder(self):
        try:
            # TODO
            print('yes')
        except Exception as e:
            self.fail(f"Should have not failed, {e}")

    def test_report_csv(self):
        try:
            report: Result = process_csv_report(folder_path="0_2025-03-15 19-14-35.D")
            print(report)
        except Exception as e:
            self.fail(f"Should have not failed: {e}")


if __name__ == '__main__':
    unittest.main()
