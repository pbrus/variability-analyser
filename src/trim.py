from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent
from varana.trim import *


argparser = ArgumentParser(
    prog='trim.py',
    description='>> Removes outstanding points from a lightcurve <<',
    epilog='Copyright (c) 2019 Przemysław Bruś',
    formatter_class=RawTextHelpFormatter
)

argparser.add_argument(
    'input_lightcurve',
    help=dedent('''\
    The name of a file which stores lightcurve data.
    ------------------------------------
    The file must contain three columns:
    time magnitude magnitude_error

    ''')
)

argparser.add_argument(
    'output_lightcurve',
    help=dedent('''\
    The name of a file which will store a filtered lightcurve.

    ''')
)

argparser.add_argument(
    '--min',
    help=dedent('''\
    The minimum value of magnitude.

    '''),
    dest='min',
    type=float,
    default=0
)

argparser.add_argument(
    '--max',
    help=dedent('''\
    The maximum value of magnitude.

    '''),
    dest='max',
    type=float,
    default=0
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
try:
    data = get_data(args.input_lightcurve)
except OSError as error:
    print(error)
    exit()

trim_data = trim(data, args.min, args.max)

if args.display:
    figure = plt.figure()
    ax = figure.add_subplot(111)
    display_plot(ax, trim_data, args.min, args.max)
    if lim != []:
        trim_data = trim(trim_data, lim[0], lim[1])

if args.image:
    if args.display and lim != []:
        trim_data = trim(trim_data, lim[0], lim[1])
        save_plot(trim_data, args.output_lightcurve, lim[0], lim[1])
    else:
        save_plot(trim_data, args.output_lightcurve, args.min, args.max)

savetxt(args.output_lightcurve, filter_lightcurve(trim_data),
        fmt="%16.6f %9.4f %7.4f")
