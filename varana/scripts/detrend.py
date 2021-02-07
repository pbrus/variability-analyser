#!/usr/bin/env python3
"""
Detrend a light curve removing seasonal and instrumental deviations.

"""
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from copy import deepcopy
from textwrap import dedent

from numpy import column_stack, savetxt

from varana.detrend import (
    akima,
    calculate_nodes_positions,
    detrend_magnitude,
    display_plot,
    load_data,
    save_plot,
    sigma_clipping_magnitude,
    too_many_points_rejected,
    validate_nodes_number,
)

arg_parser = ArgumentParser(
    prog="detrend.py",
    description=">> Remove seasonal trends from a light curve <<",
    epilog="Copyright (c) 2021 Przemysław Bruś",
    formatter_class=RawTextHelpFormatter,
)

arg_parser.add_argument(
    "input_lightcurve",
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
    "output_lightcurve",
    help=dedent(
        """\
    The name of a file which will store a detrended light curve.

    """
    ),
)

arg_parser.add_argument(
    "nodes_number",
    help=dedent(
        """\
    The number of nodes.

    """
    ),
    type=int,
)

arg_parser.add_argument(
    "--lightcurve",
    help=dedent(
        """\
    The name of a file which will store
    an additional light curve to detrend.

    """
    ),
    metavar="filename",
)

arg_parser.add_argument(
    "--sigma",
    help=dedent(
        """\
    The number (float) of standard deviations
    to filter data before trend fitting.
    (default = 3.0)

    """
    ),
    metavar="sig",
    type=float,
    default=3.0,
)

arg_parser.add_argument(
    "--display",
    help=dedent(
        """\
    Display a plot.

    """
    ),
    action="store_true",
)

arg_parser.add_argument(
    "--image",
    help=dedent(
        """\
    Save a plot to the PNG file.
    The name of the image will be the same as for output file.

    """
    ),
    action="store_true",
)

args = arg_parser.parse_args()
time, magnitude, errors = None, None, None
data, nodes_number = None, None

try:
    nodes_number = validate_nodes_number(args.nodes_number)
    data = load_data(args.input_lightcurve)
except (ArgumentTypeError, ValueError, OSError) as error:
    print(error)
    exit()

original_data = deepcopy(data)
data = sigma_clipping_magnitude(data, args.sigma)
too_many_points_rejected(args.input_lightcurve, len(original_data[1]), len(data[1]))

time, magnitude, _ = data
nodes = calculate_nodes_positions(time, magnitude, args.nodes_number)
func = akima(nodes)

if args.display:
    display_plot(time, magnitude, func, nodes)
if args.image:
    save_plot(time, magnitude, func, nodes, args.output_lightcurve)

time, magnitude, errors = original_data
detrended_magnitude = detrend_magnitude(time, magnitude, func, magnitude.mean())
savetxt(args.output_lightcurve, column_stack((time, detrended_magnitude, errors)), fmt="%18.7f %15.7f %15.7f")

if args.lightcurve:
    time, magnitude, errors = load_data(args.lightcurve)
    detrended_magnitude = detrend_magnitude(time, magnitude, func)
    savetxt(args.lightcurve, column_stack((time, detrended_magnitude, errors)), fmt="%18.7f %15.7f %15.7f")
