"""
Check whether a single frequency is made of linear combination of another frequencies.

"""
from itertools import product
from typing import Generator, List

import numpy as np


class ImproperBounds(Exception):
    """Exception throwing if the bounds of coefficients are improper."""


def coefficients_generator(
    size: int, minimum: int = -5, maximum: int = 5, max_harmonic: int = 10
) -> Generator[np.ndarray, None, None]:
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
    max_harmonic : int
        A maximum value for a harmonic. It should be greater than the upper bound of each coefficient.

    Returns
    -------
    Generator
        Cartesian product of all numbers from min to max and given size.

    Raises
    ------
    ImproperBounds
        Exception is raising when minimum >= maximum.

    """
    if minimum >= maximum:
        raise ImproperBounds(f"min={minimum} cannot be >= max={maximum}")

    range_list = list()

    for _ in range(size):
        range_list.append(range(minimum, maximum + 1))

    if maximum < max_harmonic:
        for i in range(maximum + 1, max_harmonic + 1):
            for row in i * np.eye(size, dtype=int):
                yield row

    for row in product(*range_list):
        yield np.array(row)


def get_most_likely_combination(coefficients_set: List[np.ndarray]) -> np.ndarray:
    """
    Filter a list of coefficients taking into account the most likely combination. Coefficients are chosen by
    the following rules:

        1. Leave lists of coefficients with the smallest number of non-zero elements.
        2. Filter lists leaving those with the smallest value of the sum of square coefficients, i.e. C1^2 + C2^2 + ...
        3. If still there is more than one list, choose the one that has the smallest number of negative coefficients.

    Parameters
    ----------
    coefficients_set : list
        A set of coefficient to filter

    Returns
    -------
    ndarray
        The most likely combination from the input set.

    """
    coeffs = [
        i
        for i in filter(
            lambda x: np.count_nonzero(x) == np.count_nonzero(sorted(coefficients_set, key=np.count_nonzero)[0]),
            coefficients_set,
        )
    ]
    coeffs = [
        i for i in filter(lambda x: sum(x ** 2) == sum(sorted(coeffs, key=lambda x: sum(x ** 2))[0] ** 2), coeffs)
    ]

    return sorted(coeffs, key=lambda x: sum(x < 0))[0]


def linear_combination(
    base: List[float],
    frequency: float,
    minimum: int = -5,
    maximum: int = 5,
    max_harmonic: int = 10,
    epsilon: float = 1e-5,
) -> np.ndarray:
    """
    Check whether a frequency is made of linear combination of frequencies: f0 = (C1*f1 + C2*f2 + ...)
    If is more than one choose the most likely combination.

    Parameters
    ----------
    base : List[float]
        A list of frequencies which create base of linear combination.
    frequency : float
        A single frequency which must be checked.
    minimum : int
        A lower bound of each coefficient.
    maximum : int
        An upper bound of each coefficient.
    max_harmonic : int
        A maximum value for a harmonic. It should be greater than the upper bound of each coefficient.
    epsilon : float
        If f0 - (C1*f1 + C2*f2 + ...) < epsilon, coefficients are accepted.

    Returns
    -------
    coefficients_array : ndarray
        An array with coefficients if some combination exists. Otherwise the array is filled by False.

    """
    combination_list = list()
    coefficients = coefficients_generator(len(base), minimum, maximum, max_harmonic)

    for coeff in coefficients:
        if abs(frequency - np.dot(base, coeff)) < epsilon:
            combination_list.append(coeff)

    if len(combination_list) != 0:
        return get_most_likely_combination(combination_list)
    else:
        return np.zeros(len(base), dtype=bool)
