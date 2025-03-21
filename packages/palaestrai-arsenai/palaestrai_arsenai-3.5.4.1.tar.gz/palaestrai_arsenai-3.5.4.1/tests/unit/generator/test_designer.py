import unittest
from copy import copy

import numpy as np
from arsenai.description import ParameterDefinition
from arsenai.generator import designer


class TestDesigner(unittest.TestCase):
    def setUp(self):
        ind_vars = {
            "0.environments._": {0: "test_env1", 1: "test_env2"},
            "0.agents._": {0: "test_agent1", 1: "test_agent2"},
            "0.sensors.test_agent1": {
                0: "minimal",
                1: "medium",
                2: "even_more",
                3: "all",
            },
        }
        self.pardef = ParameterDefinition()
        for key, value in ind_vars.items():
            self.pardef.add_independent_variable(key, value)

    def test_create_design_enough_runs(self):
        design = designer.create_design(self.pardef, 16)

        self.assertEqual(16, len(design))

    def test_create_design_not_enough_runs(self):
        design = designer.create_design(self.pardef, 4)

        self.assertEqual(4, len(design))

    def test_optimize(self):
        original = np.array(
            [
                [0.0, 3.0, 0.0],
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [3.0, 2.0, 3.0],
            ]
        )

        design = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ]
        )

        self.assertTrue(
            designer._isbetter(
                designer._optimize(design, original, 1000), design
            )
        )

    def test_isbetter(self):
        design1 = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [2.0, 0.0, 0.0],
            ]
        )

        design2 = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0],
                [3.0, 3.0, 3.0],
            ]
        )

        self.assertTrue(designer._isbetter(design2, design1))

    def test_mutate(self):
        original = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [2.0, 0.0, 1.0],
                [0.0, 1.0, 0.0],
                [1.0, 2.0, 3.0],
            ]
        )

        design = np.array(
            [
                [1.0, 0.0, 0.0],
                [2.0, 0.0, 1.0],
                [0.0, 1.0, 0.0],
            ]
        )

        design_copy = copy(design)
        designer._mutate(design_copy, original)
        self.assertEqual(design.shape, design_copy.shape)
        self.assertTrue(np.max(design_copy[:, 0]) <= 2)
        self.assertTrue(np.max(design_copy[:, 1]) <= 2)
        self.assertTrue(np.max(design_copy[:, 1]) <= 3)

    def test_pdist(self):
        design = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [2.0, 0.0, 1.0],
                [0.0, 1.0, 0.0],
                [1.0, 2.0, 3.0],
            ]
        )
        distences = designer._pdist(design)
        distences_expected = np.array(
            [
                1.0,
                2.23606797749979,
                1.0,
                3.7416573867739413,
                1.4142135623730951,
                1.4142135623730951,
                3.605551275463989,
                2.449489742783178,
                3.0,
                3.3166247903554,
            ]
        )
        self.assertEqual(distences.tolist(), distences_expected.tolist())


if __name__ == "__main__":
    unittest.main()
