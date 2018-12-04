#!/usr/bin/env python3

import numpy as np
from itertools import product


def coefficients_iterator(size, minimum=-10, maximum=10):
    range_list = []

    for _ in range(size):
        range_list.append(range(minimum, maximum + 1))

    for row in product(*range_list):
        yield np.array(row)

def linear_combination(frequencies, frequency, minimum=-10, maximum=10):
    coeff_iter = coefficients_iterator(len(frequencies), minimum, maximum)
    frequencies = np.array(frequencies)

    for coefficients in coeff_iter:
        if frequency == np.dot(frequencies, coefficients):
            return coefficients

    return False
