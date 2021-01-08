#!/usr/bin/env python3
"""
Check whether a single frequency is made of linear combination of another frequencies.

"""
from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent

from varana.freq_comb import linear_combination

arg_parser = ArgumentParser(
    prog="freq_comb.py",
    description=dedent(
        """\
    >> Check whether a single frequency is made
    >> of linear combination of frequencies"""
    ),
    epilog="Copyright (c) 2021 Przemysław Bruś",
    formatter_class=RawTextHelpFormatter,
)

arg_parser.add_argument(
    "--base",
    help=dedent(
        """\
    A list of basic frequencies.

    """
    ),
    nargs="+",
    metavar="f1",
    type=float,
    required=True,
)

arg_parser.add_argument(
    "--freq",
    help=dedent(
        """\
    A single frequency.

    """
    ),
    metavar="f",
    type=float,
    required=True,
)

arg_parser.add_argument(
    "--min",
    help=dedent(
        """\
    A minimum value (int) of all coefficients.
    (default = -5)

    """
    ),
    metavar="min",
    type=int,
    default=-5,
)

arg_parser.add_argument(
    "--max",
    help=dedent(
        """\
    A maximum value (int) of all coefficients.
    (default = 5)

    """
    ),
    metavar="max",
    type=int,
    default=5,
)

arg_parser.add_argument(
    "--max_harm",
    help=dedent(
        """\
    A maximum value (int) of harmonic frequencies.
    (default = 10)

    """
    ),
    metavar="harm",
    type=int,
    default=10,
)

arg_parser.add_argument(
    "--eps",
    help=dedent(
        """\
    A comparison accuracy of a single frequency
    and linear combination.
    (default = 0.00001)

    """
    ),
    metavar="eps",
    type=float,
    default=1e-5,
)

args = arg_parser.parse_args()
combination = linear_combination(args.base, args.freq, args.min, args.max, args.max_harm, args.eps)

if combination.any():
    print(*combination)
