"""
Test package of the varana.fit module
"""
import unittest
from varana.fit import *


class FitTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_approximate_sines_sum(self):
        frequencies = [1.86, 4.32, 9.31]
        parameters = [0.21, 0.15, 2.1, 0.34, 0.42, 1.8, 0.19, 0.14, 1.65]
        sines_sum = approximate_sines_sum(frequencies)
        X = [1, 2, 3, 4, 5]
        Y = [5.7377398078034165, 4.553800343955451, 5.685413814417916,
             5.941532947437767, 4.971874054636258]

        for x, y in zip(X, Y):
            self.assertEqual(sines_sum(x, *parameters), y)

    def test_amplitude(self):
        coefficients = [4, 5, 6, 7, 8]
        amplitudes = [6.4031242374328485, 7.810249675906654, 9.219544457292887,
                      10.63014581273465]

        for c1, c2, amp in zip(coefficients, coefficients[1:], amplitudes):
            coeffs = np.array([c1, c2])
            self.assertEqual(amplitude(coeffs), amp)

    def test_phase(self):
        coefficients = [55, 34, -12, 17, 6]
        phases = [0.5536813222069976, 5.943892692725542, 2.185459278717062,
                  0.3392926144540447]

        for c1, c2, ph in zip(coefficients, coefficients[1:], phases):
            coeffs = np.array([c1, c2])
            self.assertEqual(phase(coeffs), ph)

    def test_convert_linear_parameters(self):
        parameters = np.array([0.37, -0.45, 2.16, 1.21, 2.76, 1.93])
        updated_parameters = np.array([0.58258047, 5.40053395, 2.16, 3.0135859,
                                       1.15762586, 1.93])
        self.assertTrue(np.allclose(convert_linear_parameters(parameters),
                                    updated_parameters))

    def test_add_frequencies(self):
        frequencies = [3.14, 27.54, 31.96, 50.01]
        parameters = np.array([0.24, 0.54, 2.0, 0.64, 2.1, 3.0, 0.54, 0.86,
                               1.1, 0.43, 1.2, 0.7])
        results = np.array([
            [0.24, 3.14, 0.54, 2.0],
            [0.64, 27.54, 2.1, 3.0],
            [0.54, 31.96, 0.86, 1.1],
            [0.43, 50.01, 1.2, 0.7]
        ])
        self.assertTrue(np.allclose(add_frequencies(parameters, frequencies),
                                    results))
