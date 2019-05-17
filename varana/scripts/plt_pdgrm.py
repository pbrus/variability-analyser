#!/usr/bin/env python3

from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from textwrap import dedent
from varana.plt_pdgrm import *


argparser = ArgumentParser(
    prog='plt_pdgrm.py',
    description='>> Display a periodogram <<',
    epilog='Copyright (c) 2019 Przemysław Bruś',
    formatter_class=RawTextHelpFormatter
)

argparser.add_argument(
    'periodogram',
    help=dedent('''\
    The name of a file which stores a periodogram.
    ------------------------------------
    The file must contain two columns:
    frequency amplitude

    ''')
)

argparser.add_argument(
    '--display',
    help=dedent('''\
    Display a periodogram.

    '''),
    action='store_true'
)

argparser.add_argument(
    '--image',
    help=dedent('''\
    Save a periodogram to the PNG file.

    '''),
    metavar="filename",
    type=str,
    default=None
)

args = argparser.parse_args()

try:
    frequency, amplitude = get_data(args.periodogram)
except (ArgumentTypeError, OSError) as error:
    print(error)
    exit()

if args.display:
    display_periodogram(frequency, amplitude)

if args.image:
    save_periodogram(frequency, amplitude, args.image)
