#!/usr/bin/env python3
"""
Display or save a periodogram to a file.

"""
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from textwrap import dedent

from varana.plt_pdgrm import display_periodogram, get_data, save_periodogram

arg_parser = ArgumentParser(
    prog="plt_pdgrm.py",
    description=">> Display a periodogram <<",
    epilog="Copyright (c) 2021 Przemysław Bruś",
    formatter_class=RawTextHelpFormatter,
)

arg_parser.add_argument(
    "periodogram",
    help=dedent(
        """\
    The name of a file with periodogram.
    ------------------------------------
    The file must contain two columns:
    frequency amplitude

    """
    ),
)

arg_parser.add_argument(
    "--display",
    help=dedent(
        """\
    Display a periodogram.

    """
    ),
    action="store_true",
)

arg_parser.add_argument(
    "--image",
    help=dedent(
        """\
    Save a periodogram to the PNG file.

    """
    ),
    metavar="filename",
    type=str,
    default=None,
)

args = arg_parser.parse_args()
frequency, amplitude = None, None

try:
    frequency, amplitude = get_data(args.periodogram)
except (ArgumentTypeError, OSError) as error:
    print(error)
    exit()

if args.display:
    display_periodogram(frequency, amplitude)

if args.image:
    save_periodogram(frequency, amplitude, args.image)
