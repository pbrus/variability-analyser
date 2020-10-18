"""
Test package for varana.freq_comb module.

"""
import unittest

import numpy as np

from varana.freq_comb import coefficients_generator, linear_combination


class FreqCombTest(unittest.TestCase):
    def test_coefficients_generator(self):
        coeff_gen = coefficients_generator(3)
        index = (2349, 5742, 8677)
        results = (np.array([-5, -4, 8]), np.array([3, -10, -1]), np.array([9, 4, -6]))

        for i, (idx, cg, res) in enumerate(zip(index, coeff_gen, results)):
            if i == idx:
                self.assertTrue((cg == res).any())

    def test_linear_combination(self):
        base = [1.64, 2.53, 7.85]
        frequencies = (7.71, 17.97, 10.09, 23.9)
        results = (np.array([3, -2, 1]), np.array([0, 4, 1]), np.array([False, False, False]), np.array([5, 0, 2]))

        for freq, res in zip(frequencies, results):
            self.assertTrue((linear_combination(base, freq) == res).any())
