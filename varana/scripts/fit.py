#!/usr/bin/env python3
"""
Fit a sum of sines to the light curve.

"""
from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent

from numpy import genfromtxt

from varana.fit import fit_final_curve, print_parameters, save_residuals

arg_parser = ArgumentParser(
    prog="fit.py",
    description=">> Fit a sum of sines to the light curve <<",
    epilog="Copyright (c) 2021 Przemysław Bruś",
    formatter_class=RawTextHelpFormatter,
)

arg_parser.add_argument(
    "lightcurve",
    help=dedent(
        """\
    The name of a file which stores light curve data.
    ------------------------------------
    The file must contain three columns:
    time magnitude magnitude_error

    """
    ),
)

arg_parser.add_argument(
    "--freq",
    help=dedent(
        """\
    A list of frequencies for each sine.

    """
    ),
    nargs="+",
    metavar="f1",
    type=float,
    required=True,
)

arg_parser.add_argument(
    "--resid",
    help=dedent(
        """\
    A name of the file storing residuals.

    """
    ),
    metavar="filename",
    type=str,
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
    Accuracy of comparison of frequencies.
    (default = 0.00001)

    """
    ),
    metavar="eps",
    type=float,
    default=1e-5,
)

args = arg_parser.parse_args()
lightcurve = None

try:
    lightcurve = genfromtxt(args.lightcurve)
except OSError as error:
    print(error)
    exit()

frequencies = sorted(args.freq)
parameters = fit_final_curve(lightcurve, frequencies, args.min, args.max, args.max_harm, args.eps)
print_parameters(parameters)

if args.resid is not None:
    save_residuals(lightcurve, parameters, args.resid)
