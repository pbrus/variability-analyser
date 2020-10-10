"""
Check whether a single frequency is made of linear combination of another
frequencies.

"""
from itertools import product
from typing import Generator

import numpy as np
from numpy import ndarray


def coefficients_generator(size: int, minimum: int = -10, maximum: int = 10) -> Generator[ndarray, None, None]:
    """
    Create a generator of coefficients of linear combination of frequencies,
    i.e. C1, C2, C3, ...: (C1*f1 + C2*f2 + ...)

    Parameters
    ----------
    size : int
        A size of the base.
    minimum : int
        A lower bound of each coefficient.
    maximum : int
        An upper bound of each coefficient.

    Returns
    -------
    Generator
        Cartesian product of all numbers from min to max and given size.

    """
    range_list = list()

    for _ in range(size):
        range_list.append(range(minimum, maximum + 1))

    for row in product(*range_list):
        yield np.array(row)


def linear_combination(
    frequencies: list, frequency: float, minimum: int = -10, maximum: int = 10, epsilon: float = 1e-3
) -> ndarray:
    """
    Check whether a frequency is made of linear combination of frequencies:
    f0 = (C1*f1 + C2*f2 + ...). If it is, choose the one which minimizes a sum of square values.

    Parameters
    ----------
    frequencies : list
        A list of frequencies which create base of linear combination.
    frequency : float
        A single frequency which must be checked.
    minimum : int
        A lower bound of each coefficient.
    maximum : int
        An upper bound of each coefficient.
    epsilon : float
        If f0 - (C1*f1 + C2*f2 + ...) < epsilon, coefficients are accepted.

    Returns
    -------
    coefficients_array : ndarray
        An array with coefficients.

    """
    coeff_iter = coefficients_generator(len(frequencies), minimum, maximum)
    frequencies = np.array(frequencies)
    coefficients_array = np.zeros(len(frequencies), dtype=bool)
    coeff_sum = np.inf

    for coefficients in coeff_iter:
        if abs(frequency - np.dot(frequencies, coefficients)) < epsilon:
            current_coeff_sum = np.power(coefficients, 2).sum()
            if current_coeff_sum < coeff_sum:
                coeff_sum = current_coeff_sum
                coefficients_array = coefficients

    return coefficients_array
