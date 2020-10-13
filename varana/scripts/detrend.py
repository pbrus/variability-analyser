#!/usr/bin/env python3
"""
Detrend a light curve removing seasonal deviations.

"""
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from copy import deepcopy
from textwrap import dedent

from numpy import savetxt

from varana.detrend import (
    calculate_kmeans,
    detrend_data,
    display_plot,
    get_data,
    save_plot,
    sigma_clipping_magnitude,
    sorted_centers,
    spline_function,
    spline_order,
    too_much_points_rejected,
    unpack_data,
    valid_seasons_amount,
    warn_rejected_points,
    x_domain_spline,
)

arg_parser = ArgumentParser(
    prog="detrend.py",
    description=">> Remove seasonal trends from a light curve <<",
    epilog="Copyright (c) 2020 Przemysław Bruś",
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
    "seasons_amount",
    help=dedent(
        """\
    The number of seasons in the data.
    The seasons are separated by time-gaps in the data.

    """
    ),
    type=int,
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
data, seasons_amount = None, None

try:
    seasons_amount = valid_seasons_amount(args.seasons_amount)
    data = get_data(args.input_lightcurve)
except (ArgumentTypeError, OSError) as error:
    print(error)
    exit()

org_data = deepcopy(data)
data = sigma_clipping_magnitude(data)

if too_much_points_rejected(len(org_data), len(data)):
    warn_rejected_points(args.input_lightcurve)

time, magnitude, error_magnitude = unpack_data(data)
kmeans = calculate_kmeans(time, magnitude, error_magnitude, seasons_amount)
centers = sorted_centers(kmeans)
spline = spline_function(centers, spline_order(seasons_amount))
x_spline = x_domain_spline(time)
y_spline = spline(x_spline)
spline_coordinates = x_spline, y_spline

if args.display:
    display_plot(time, magnitude, spline_coordinates, centers)
if args.image:
    save_plot(time, magnitude, spline_coordinates, centers, args.output_lightcurve)

detrended_data = detrend_data(org_data, spline, magnitude.mean())
savetxt(args.output_lightcurve, detrended_data, fmt="%18.7f %15.7f %15.7f")
