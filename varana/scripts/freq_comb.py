#!/usr/bin/env python3

from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent
from varana.freq_comb import *


argparser = ArgumentParser(
    prog='freq_comb.py',
    description=dedent('''\
    >> Check whether a single frequency is made of
    >> linear combination of frequencies'''),
    epilog='Copyright (c) 2019 Przemysław Bruś',
    formatter_class=RawTextHelpFormatter
)

argparser.add_argument(
    '--base',
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

argparser.add_argument(
    '--min',
    help=dedent('''\
    A minimum value (int) of all coefficients.
    (default = -10)

    '''),
    metavar='min',
    type=int,
    default=-10
)

argparser.add_argument(
    '--max',
    help=dedent('''\
    A maximum value (int) of all coefficients.
    (default = 10)

    '''),
    metavar='max',
    type=int,
    default=10
)

argparser.add_argument(
    '--eps',
    help=dedent('''\
    A comparison accuracy of a single frequency
    and linear combination.
    (default = 0.001)

    '''),
    metavar='eps',
    type=float,
    default=1e-3
)

args = argparser.parse_args()
combination = linear_combination(args.base, args.freq,
                                 minimum=args.min, maximum=args.max,
                                 epsilon=args.eps)

if combination.any():
    print(*combination)
