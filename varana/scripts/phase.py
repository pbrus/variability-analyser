#!/usr/bin/env python3

from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from textwrap import dedent
from varana.phase import *


argparser = ArgumentParser(
    prog='phase.py',
    description='>> Phase a light curve <<',
    epilog='Copyright (c) 2019 Przemysław Bruś',
    formatter_class=RawTextHelpFormatter
)

argparser.add_argument(
    'lightcurve',
    help=dedent('''\
    The name of a file which stores light curve data.
    ------------------------------------
    The file must contain three columns:
    time magnitude magnitude_error

    ''')
)

argparser.add_argument(
    'frequency',
    help=dedent('''\
    A value of frequency which phases the light curve with.

    '''),
    type=float
)

argparser.add_argument(
    '-p',
    help=dedent('''\
    The positional argument "frequency" is a period.

    '''),
    action='store_true'
)

argparser.add_argument(
    '--phase',
    help=dedent('''\
    The number of phases.
    (default = 2)

    '''),
    metavar="N",
    type=int,
    default=2
)

argparser.add_argument(
    '--model',
    help=dedent('''\
    A name of the file with a model defined as:

    y_intercept
    amplitude1 frequency1 phase1
    amplitude2 frequency2 phase2
    amplitude3 frequency3 phase3
    ...

    The amplitude, frequency and phase describe a single sine
    which the model is made of.

    '''),
    metavar="filename",
    type=str
)

argparser.add_argument(
    '--save',
    help=dedent('''\
    Save the phased light curve to the file.

    '''),
    metavar="filename",
    type=str
)

argparser.add_argument(
    '--display',
    help=dedent('''\
    Display a plot.

    '''),
    action='store_true'
)

argparser.add_argument(
    '--image',
    help=dedent('''\
    Save a plot to the PNG file.
    The name of the image will be the same as for output file.

    '''),
    action='store_true'
)

args = argparser.parse_args()

if args.p:
    frequency = 1/args.frequency
else:
    frequency = args.frequency

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
