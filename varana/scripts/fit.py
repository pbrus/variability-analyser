from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent
from varana.fit import *


argparser = ArgumentParser(
    prog='fit.py',
    description='>> Fit a sum of sines to the light curve <<',
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
    '--freq',
    help=dedent('''\
    A list of frequencies for each sine.

    '''),
    nargs='+',
    metavar='f1',
    type=float,
    required=True
)

argparser.add_argument(
    '--resid',
    help=dedent('''\
    A name of the file storing residuals.

    '''),
    metavar='filename',
    type=str
)

argparser.add_argument(
    '--eps',
    help=dedent('''\
    Accuracy of comparison of frequencies.
    (default = 0.001)

    '''),
    metavar='eps',
    type=float,
    default=1e-3
)

args = argparser.parse_args()
try:
    lightcurve = np.genfromtxt(args.lightcurve)
except OSError as error:
    print(error)
    exit()

frequencies = sorted(args.freq)
parameters = fit_final_curve(lightcurve, frequencies, args.eps)
print_parameters(parameters)

if args.resid is not None:
    save_residuals(lightcurve, parameters, args.resid)
