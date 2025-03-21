import os
import shutil
import unittest

import ruamel.yaml as yml
from arsenai.api import fnc_generate


class TestCase01SingleRun(unittest.TestCase):
    def setUp(self) -> None:
        fixtures_path = os.path.abspath(
            os.path.join(__file__, "..", "..", "fixtures")
        )
        self.experiment_file = os.path.join(
            fixtures_path, "testcase01_single_run.yml"
        )
        self.expected_run_file = os.path.join(
            fixtures_path, "testcase01_single_run_expected.yml"
        )
        self.tmp_path = os.path.abspath(os.path.join(os.getcwd(), "tmp"))
        self.actual_run_file = os.path.join(
            self.tmp_path, "TestCase01-SingleRun_run-0.yml"
        )

    def test_generate(self):
        with open(self.expected_run_file, "r") as yml_file:
            expected = yml.YAML(typ="safe", pure=True).load(yml_file)

        try:
            fnc_generate.generate(self.experiment_file)
        except SystemExit:
            pass

        with open(self.actual_run_file, "r") as yml_file:
            actual = yml.YAML(typ="safe", pure=True).load(yml_file)

        self.maxDiff = None
        self.assertDictEqual(expected, actual)

    def tearDown(self):
        shutil.rmtree(self.tmp_path)


if __name__ == "__main__":
    unittest.main()
