"""
Test package for varana.freq_comb module.

"""
import unittest

import numpy as np
import pytest

from varana.freq_comb import coefficients_generator, ImproperBounds, get_most_likely_combination, linear_combination


def test_coefficient_generator_exception():
    with pytest.raises(ImproperBounds):
        next(coefficients_generator(3, 1, -1, 4))


@pytest.mark.parametrize(
    "size, min, max, harm_max, n, result",
    [
        (2, -2, 2, 5, 1, np.array([3, 0])),
        (2, -2, 2, 5, 3, np.array([4, 0])),
        (2, -2, 2, 5, 6, np.array([0, 5])),
        (2, -2, 2, 5, 9, np.array([-2, 0])),
        (3, -1, 1, 4, 1, np.array([2, 0, 0])),
        (3, -1, 1, 4, 3, np.array([0, 0, 2])),
        (3, -1, 1, 4, 4, np.array([3, 0, 0])),
        (3, -1, 1, 4, 8, np.array([0, 4, 0])),
        (3, -1, 1, 4, 10, np.array([-1, -1, -1])),
        (3, -1, 1, 4, 20, np.array([0, -1, 0])),
        (4, -2, 2, 1, 1, np.array([-2, -2, -2, -2])),
        (2, 0, 5, 4, 6, np.array([0, 5])),
    ],
)
def test_coefficients_generator(size, min, max, harm_max, n, result):
    for i, coefficients in enumerate(coefficients_generator(size, min, max, harm_max)):
        if (i + 1) == n:
            assert (coefficients == result).all()


@pytest.mark.parametrize(
    "coefficients_set, result",
    [
        ([np.array([4, 1, -2]), np.array([3, -5, 2]), np.array([1, -2, 9])], np.array([4, 1, -2])),
        ([np.array([2, 1]), np.array([-2, 1]), np.array([-1, 2]), np.array([-1, -2])], np.array([2, 1])),
        (
            [
                np.array([3, 4, 5]),
                np.array([3, -4, 9]),
                np.array([2, 8]),
                np.array([1, 1]),
                np.array([3]),
                np.array([9]),
            ],
            np.array([3]),
        ),
        ([np.array([2, 1])], np.array([2, 1])),
    ],
)
def test_get_most_likely_combination(coefficients_set, result):
    assert (get_most_likely_combination(coefficients_set) == result).all()


class FreqCombTest(unittest.TestCase):
    def test_linear_combination(self):
        base = [1.64, 2.53, 7.85]
        frequencies = (7.71, 17.97, 10.09, 23.9)
        results = (np.array([3, -2, 1]), np.array([0, 4, 1]), np.array([False, False, False]), np.array([5, 0, 2]))

        for freq, res in zip(frequencies, results):
            self.assertTrue((linear_combination(base, freq) == res).all())
