"""
Test package for varana.freq_comb module.

"""
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
        ([np.array([4, 0, 1, -2]), np.array([0, 3, -5, 2]), np.array([1, -2, 9, -4])], np.array([4, 0, 1, -2])),
        ([np.array([-2, 1]), np.array([2, 1]), np.array([-1, 2]), np.array([-1, -2])], np.array([2, 1])),
        (
            [
                np.array([3, 4, 5]),
                np.array([3, -4, 9]),
                np.array([0, 2, 8]),
                np.array([1, 0, 1]),
                np.array([0, 3, 0]),
                np.array([9, 0, 0]),
            ],
            np.array([0, 3, 0]),
        ),
        ([np.array([2, 1])], np.array([2, 1])),
    ],
)
def test_get_most_likely_combination(coefficients_set, result):
    assert (get_most_likely_combination(coefficients_set) == result).all()


@pytest.mark.parametrize(
    "base, frequency, min, max, max_harm, result",
    [
        ([0.55, 1.10, 2.48, 3.87], 5.78, 0, 3, 3, np.array([0, 3, 1, 0])),
        ([0.21, 0.49, 0.98, 5.03], 0.14, -1, 3, 3, np.array([3, -1, 0, 0])),
        ([3.14, 6.28], 21.98, 0, 1, 7, np.array([7, 0])),
        ([0.12, 1.09, 1.59], 10.00, -5, 5, 10, np.array([False, False, False])),
        ([1.64, 2.53, 7.85, 9.11], -1.26, -1, 1, 1, np.array([0, 0, 1, -1])),
        ([1.64, 2.53, 7.85], 7.71, -2, 3, 3, np.array([3, -2, 1])),
        ([1.64, 2.53, 7.85], 17.97, 0, 4, 4, np.array([0, 4, 1])),
        ([1.64, 2.53, 7.85], 10.09, -5, 5, 10, np.array([False, False, False])),
        ([1.64, 2.53, 7.85], 23.90, -5, 5, 10, np.array([5, 0, 2])),
    ],
)
def test_linear_combination(base, frequency, min, max, max_harm, result):
    assert (linear_combination(base, frequency, min, max, max_harm) == result).all()
