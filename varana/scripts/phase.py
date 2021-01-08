#!/usr/bin/env python3
"""
Phase a light curve with a specific frequency.

"""
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from textwrap import dedent

from varana.phase import display_plot, get_model, prepare_data, save_phased_lightcurve, save_plot

arg_parser = ArgumentParser(
    prog="phase.py",
    description=">> Phase a light curve <<",
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
    "frequency",
    help=dedent(
        """\
    A value of frequency which phases the light curve with.

    """
    ),
    type=float,
)

arg_parser.add_argument(
    "-p",
    help=dedent(
        """\
    The positional argument "frequency" is a period.

    """
    ),
    action="store_true",
)

arg_parser.add_argument(
    "--phase",
    help=dedent(
        """\
    The number of phases.
    (default = 2)

    """
    ),
    metavar="N",
    type=int,
    default=2,
)

arg_parser.add_argument(
    "--model",
    help=dedent(
        """\
    A name of the file with a model defined as:

    y_intercept
    amplitude1 frequency1 phase1
    amplitude2 frequency2 phase2
    amplitude3 frequency3 phase3
    ...

    The amplitude, frequency and phase describe a single sine
    which the model is made of.

    """
    ),
    metavar="filename",
    type=str,
)

arg_parser.add_argument(
    "--save",
    help=dedent(
        """\
    Save the phased light curve to the file.

    """
    ),
    metavar="filename",
    type=str,
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

if args.p:
    frequency = 1 / args.frequency
else:
    frequency = args.frequency

phase, magnitude, model = None, None, None

try:
    phase, magnitude = prepare_data(args.lightcurve, frequency, args.phase)
    if args.model:
        model = get_model(args.model, frequency, phase, magnitude)
    else:
        model = None
except (ArgumentTypeError, OSError) as error:
    print(error)
    exit()

if args.save:
    save_phased_lightcurve(phase, magnitude, args.save)

if args.display:
    display_plot(phase, magnitude, model)

if args.image:
    save_plot(phase, magnitude, args.lightcurve, model)
