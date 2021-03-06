"""
Test package for varana.fit module.

"""
import unittest
from os.path import realpath, split

import numpy as np
import pytest

from varana.fit import (
    add_frequencies,
    amplitude,
    approximate_parameters,
    approximate_sines_sum,
    convert_linear_parameters,
    final_parameters,
    final_sines_sum,
    fit_approximate_curve,
    fit_final_curve,
    frequencies_combination,
    initial_sines_sum_parameters,
    normalize_phase,
    phase,
    sines_sum,
    split_frequencies,
    substract_model,
)


@pytest.mark.parametrize(
    "frequencies, min_coeff, max_coeff, max_harm, epsilon, result",
    [
        ([0.7548, 3.7741, 1.2916, 2.8011, 6.0384], -2, 5, 10, 1.1e-4, ([0.7548, 1.2916], [2.8011, 3.7741, 6.0384])),
        ([6.0384, 3.7741, 1.2916, 2.8011, 0.7548], -2, 5, 10, 1.1e-6, ([0.7548, 1.2916, 2.8011, 3.7741], [6.0384])),
        ([0.7548, 6.0384, 3.7741, 2.8011, 1.2916], 0, 5, 6, 1.1e-4, ([0.7548, 1.2916, 6.0384], [2.8011, 3.7741])),
        ([0.8741, 5.6310, 0.5631], -5, 5, 10, 1e-4, ([0.5631, 0.8741], [5.6310])),
        ([5.6310, 0.5631, 0.8741], -5, 5, 5, 1e-4, ([0.5631, 0.8741, 5.6310], [])),
        ([1.1111, 0.8741, 0.5631], -2, 2, 2, 1.1e-4, ([0.5631, 0.8741, 1.1111], [])),
    ],
)
def test_split_frequencies(frequencies, min_coeff, max_coeff, max_harm, epsilon, result):
    assert split_frequencies(frequencies, min_coeff, max_coeff, max_harm, epsilon) == result


@pytest.mark.parametrize(
    "frequencies, min_coeff, max_coeff, max_harm, epsilon, result",
    [
        (
            [0.7548, 3.7741, 1.2916, 2.8011, 6.0384],
            -2,
            5,
            10,
            1.1e-4,
            ([0.7548, 1.2916], np.array([[1, 0], [0, 1], [2, 1], [5, 0], [8, 0]])),
        ),
        (
            [6.0384, 3.7741, 1.2916, 2.8011, 0.7548],
            -2,
            5,
            10,
            1.1e-6,
            (
                [0.7548, 1.2916, 2.8011, 3.7741],
                np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [8, 0, 0, 0]]),
            ),
        ),
        (
            [0.7548, 6.0384, 3.7741, 2.8011, 1.2916],
            0,
            5,
            6,
            1.1e-4,
            ([0.7548, 1.2916, 6.0384], np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [2, 1, 0], [5, 0, 0]])),
        ),
        ([0.8741, 5.6310, 0.5631], -5, 5, 10, 1e-4, ([0.5631, 0.8741], np.array([[1, 0], [0, 1], [10, 0]]))),
        (
            [5.6310, 0.5631, 0.8741],
            -5,
            5,
            5,
            1e-4,
            ([0.5631, 0.8741, 5.6310], np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])),
        ),
        (
            [1.1111, 0.8741, 0.5631],
            -2,
            2,
            2,
            1.1e-4,
            ([0.5631, 0.8741, 1.1111], np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])),
        ),
    ],
)
def test_frequencies_combination(frequencies, min_coeff, max_coeff, max_harm, epsilon, result):
    base, combination = frequencies_combination(frequencies, min_coeff, max_coeff, max_harm, epsilon)
    assert base == result[0]
    assert (combination == result[1]).all()


class FitTest(unittest.TestCase):
    def setUp(self):
        path = split(realpath(__file__))[0]
        self.lc_filename = path + r"/test_data/synthetic_lc_1.dat"
        self.lightcurve = np.genfromtxt(self.lc_filename)
        self.frequencies = [15.24, 30.48, 40.29]

    def test_approximate_sines_sum(self):
        frequencies = [1.86, 4.32, 9.31]
        parameters = [0.21, 0.15, 2.1, 0.34, 0.42, 1.8, 0.19, 0.14, 1.65]
        sines_sum = approximate_sines_sum(frequencies)
        xx = [1, 2, 3, 4, 5]
        yy = [5.7377398078034165, 4.553800343955451, 5.685413814417916, 5.941532947437767, 4.971874054636258]

        for x, y in zip(xx, yy):
            self.assertAlmostEqual(sines_sum(x, *parameters), y)

    def test_amplitude(self):
        coefficients = [4, 5, 6, 7, 8]
        amplitudes = [6.4031242374328485, 7.810249675906654, 9.219544457292887, 10.63014581273465]

        for c1, c2, amp in zip(coefficients, coefficients[1:], amplitudes):
            coeffs = np.array([c1, c2])
            self.assertEqual(amplitude(coeffs), amp)

    def test_phase(self):
        coefficients = [55, 34, -12, 17, 6]
        phases = [0.5536813222069976, 5.943892692725542, 2.185459278717062, 0.3392926144540447]

        for c1, c2, ph in zip(coefficients, coefficients[1:], phases):
            coeffs = np.array([c1, c2])
            self.assertEqual(phase(coeffs), ph)

    def test_convert_linear_parameters(self):
        parameters = np.array([0.37, -0.45, 2.16, 1.21, 2.76, 1.93])
        updated_parameters = np.array([0.58258047, 5.40053395, 2.16, 3.0135859, 1.15762586, 1.93])
        self.assertTrue(np.allclose(convert_linear_parameters(parameters), updated_parameters))

    def test_add_frequencies(self):
        frequencies = [3.14, 27.54, 31.96, 50.01]
        parameters = np.array([0.24, 0.54, 2.0, 0.64, 2.1, 3.0, 0.54, 0.86, 1.1, 0.43, 1.2, 0.7])
        results = np.array(
            [[0.24, 3.14, 0.54, 2.0], [0.64, 27.54, 2.1, 3.0], [0.54, 31.96, 0.86, 1.1], [0.43, 50.01, 1.2, 0.7]]
        )
        self.assertTrue(np.allclose(add_frequencies(parameters, frequencies), results))

    def test_fit_approximate_curve(self):
        results = np.array([-0.2494923, -0.01925816, 0.10011763, 0.04501172, -0.05573333, 0.02322433])
        self.assertTrue(
            np.allclose(np.delete(fit_approximate_curve(self.lightcurve, self.frequencies), [2, 5, 8]), results)
        )

    def test_approximate_parameters(self):
        results = np.array(
            [
                [2.50234459e-01, 1.52400000e01, 3.21862930e00],
                [1.09770643e-01, 3.04800000e01, 4.22511514e-01],
                [6.03785842e-02, 4.02900000e01, 2.74676921e00],
            ]
        )
        self.assertTrue(np.allclose(approximate_parameters(self.lightcurve, self.frequencies)[:, :-1], results))

    def test_final_sines_sum(self):
        linear_comb = np.array([[1, 0], [0, 1], [2, -1]])
        parameters = np.array(
            [0.28586711, 0.07301911, 0.79940148, 0.54837315, 0.23782887, 0.80846081, 0.06918676, 0.22500815, 0.96334566]
        )
        results = np.array(
            [
                1.567513682748982,
                1.7472277937423941,
                0.5403788490096673,
                0.8725647092149394,
                1.883750268101744,
                0.8766700568767499,
            ]
        )
        func = final_sines_sum(linear_comb)

        for x, y in zip(range(6), results):
            self.assertAlmostEqual(func(x, *parameters), y)

    def test_initial_sines_sum_parameters(self):
        parameters = approximate_parameters(self.lightcurve, self.frequencies)
        results = np.array(
            [
                1.52400000e01,
                3.04800000e01,
                4.02900000e01,
                2.50234459e-01,
                3.21862930e00,
                1.09770643e-01,
                4.22511514e-01,
                6.03785842e-02,
                2.74676921e00,
                7.22373641e-05,
            ]
        )
        self.assertTrue(np.allclose(initial_sines_sum_parameters(parameters, self.frequencies), results))

    def test_fit_final_curve(self):
        results = np.array(
            [
                6.44061473e-05,
                2.50203690e-01,
                1.52400005e01,
                3.21754473e00,
                6.03817975e-02,
                4.02899929e01,
                2.76319565e00,
                1.09771506e-01,
                3.04800010e01,
                4.20315650e-01,
            ]
        )
        fitting = fit_final_curve(self.lightcurve, self.frequencies, -1, 1, 2)
        self.assertTrue(np.allclose(fitting, results))

    def test_final_parameters(self):
        linear_comb = np.array([[1, 0], [0, 1], [2, 0]])
        parameters = np.array(
            [
                1.52400005e01,
                4.02899929e01,
                2.50203690e-01,
                3.21754473e00,
                6.03817975e-02,
                2.76319565e00,
                1.09771506e-01,
                4.20315650e-01,
                6.44061473e-05,
            ]
        )
        results = np.array(
            [
                6.44061473e-05,
                2.50203690e-01,
                1.52400005e01,
                3.21754473e00,
                6.03817975e-02,
                4.02899929e01,
                2.76319565e00,
                1.09771506e-01,
                3.04800010e01,
                4.20315650e-01,
            ]
        )
        self.assertTrue(np.allclose(final_parameters(parameters, linear_comb), results))

    def test_normalize_phase(self):
        phases = [-7.23516, -3.27864, 1.25784, 6.93467, 12.57866]
        results = [5.331210614359173, 3.004545307179586, 1.25784, 0.6514846928204134, 0.012289385640826822]

        for phase, res in zip(phases, results):
            self.assertAlmostEqual(normalize_phase(phase), res)

    def test_sines_sum(self):
        parameters = np.array(
            [
                7.09037474,
                0.69180504,
                0.48045832,
                0.91649189,
                0.03522788,
                0.99134144,
                0.1823759,
                0.87827656,
                0.07623589,
                0.18287043,
            ]
        )
        func = sines_sum(parameters)
        results = np.array(
            [
                7.80540857239703,
                7.141428500939401,
                8.321419660720451,
                7.607768552801675,
                8.133232982571016,
                7.350358898603323,
            ]
        )

        for x, y in zip(range(6), results):
            self.assertAlmostEqual(func(x), y)

    def test_substract_model(self):
        xx = np.array(
            [
                [8.60894124, 4.84796116],
                [4.86342238, 8.6790649],
                [7.6383126, 11.0187499],
                [2.54346889, 14.07259265],
                [16.81049481, 15.46200385],
                [7.91546894, 22.63471038],
                [19.91244385, 5.52959931],
                [12.74807862, 14.68310567],
            ]
        )
        yy = np.array(
            [
                [8.60894124, -39.43908444],
                [4.86342238, 3.61645477],
                [7.6383126, -20.41013166],
                [2.54346889, 19.23376533],
                [16.81049481, -212.69924745],
                [7.91546894, -12.27353131],
                [19.91244385, -327.23848907],
                [12.74807862, -105.5861669],
            ]
        )

        def _func(x):
            return x ** 2 - 3 * x - 4

        self.assertTrue(np.allclose(substract_model(xx, _func), yy))

    def tearDown(self):
        self.lc_filename = None
        self.lightcurve = None
        self.frequencies = None
