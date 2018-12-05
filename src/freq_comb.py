#!/usr/bin/env python3

import numpy as np
from itertools import product
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from textwrap import dedent


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


if __name__ == "__main__":
    argparser = ArgumentParser(
        prog='freq_comb.py',
        description=dedent('''\
        >> Check whether a single frequency is made of
        >> linear combination of frequencies'''),
        epilog='Copyright (c) 2018 Przemysław Bruś',
        formatter_class=RawTextHelpFormatter
    )

    argparser.add_argument(
        '--basic_freq',
        help=dedent('''\
        A list of basic frequencies.

        '''),
        nargs='+',
        metavar='f1',
        type=float,
        required=True
    )

    argparser.add_argument(
        '--freq',
        help=dedent('''\
        A single frequency.

        '''),
        metavar='f',
        type=float,
        required=True
    )

    args = argparser.parse_args()