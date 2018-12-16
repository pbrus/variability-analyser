#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from copy import deepcopy
from warnings import filterwarnings
from os.path import basename, splitext, dirname, join
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from textwrap import dedent

filterwarnings("ignore",
               message="Covariance of the parameters could not be estimated")


def read_lightcurve(filename):
    """
    Read a lightcurve from a file.

    Parameters
    ----------
    filename : str
        The name of the file.

    Returns
    -------
    tuple
        Each element represents a single column.
    """
    return np.loadtxt(filename, unpack=True)

def read_model(filename):
    """
    Read a model from a file. The model is defined as:

    y_intercept
    amplitude1 frequency1 phase1
    amplitude2 frequency2 phase2
    amplitude3 frequency3 phase3
    ...

    The amplitude, frequency and phase describe a single sine which
    the model is made of.

    Parameters
    ----------
    filename : str
        The name of the file.

    Returns
    -------
    tuple
        The first element is a y intercept of the model, the second one is an
        ndarray which stores parameters of each sine.
    """
    y_intercept = np.genfromtxt(filename, max_rows=1)
    parameters = np.genfromtxt(filename, skip_header=1)

    return y_intercept, parameters

def time_to_phase(time, period):
    """
    Convert time to phase.

    Parameters
    ----------
    time : ndarray
        An array which represents a time vector.
    period : float
        A value of period which phases the lightcurve with.

    Returns
    -------
    phase
        A phase vector.
    """
    time_min = time.min()
    time = time - time_min
    phase = time/period - time//period

    return phase

def multiply_phase(phase, magnitude, factor):
    """
    Multiply a phase vector by the factor.

    Parameters
    ----------
    phase : ndarray
        An array which represents a phase vector.
    magnitude : ndarray
        An array which represents a magnitude vector.
    factor : int
        A number indicating how many phases to display.

    Returns
    -------
    tuple
        A tuple made of phase and magnitude vectors.
    """
    single_phase = deepcopy(phase)
    single_magnitude = deepcopy(magnitude)

    for i in range(1, factor):
        phase = np.append(phase, single_phase + i)
        magnitude = np.append(magnitude, single_magnitude)

    return phase, magnitude

def prepare_data(filename, frequency, phases_number):
    """
    Phase a lightcurve with the frequency.

    Parameters
    ----------
    filename : str
        A name of a file which stores a lightcurve.
    frequency : float
        A value of the frequeny which phases the lightcurve with.
    phases_number : int
        A number indicating how many phases to display.

    Returns
    -------
    tuple
        A tuple made of phase and magnitude vectors.
    """
    time, magnitude, _ = read_lightcurve(filename)
    phase = time_to_phase(time, 1/frequency)
    phase, magnitude = multiply_phase(phase, magnitude, phases_number)

    return phase, magnitude

def get_model(filename, frequency, phase, magnitude):
    """
    Get a model in XY coordinates and align it to the phased lightcurve.

    Parameters
    ----------
    filename : str
        A name of a file which stores a model.
    frequency : float
        A value of the frequeny which phases the lightcurve with.
    phase : ndarray
        An array which stores a phase vector.
    magnitude : ndarray
        An array which represents a magnitude vector.

    Returns
    -------
    tuple
        A tuple made of X, Y coordinates.
    """
    y_intercept, parameters = read_model(filename)
    min_phase, max_phase = round(phase.min()), round(phase.max())
    approx_sines_sum = sines_sum(parameters, y_intercept, frequency)
    x0, _ = curve_fit(approx_sines_sum, phase, magnitude, p0=0)
    X = np.linspace(min_phase, max_phase, max_phase*100)
    model = sines_sum(parameters, y_intercept, frequency)

    return X, model(X, x0)

def sines_sum(sines_parameters, y_intercept, frequency):
    """
    Define a sum of sines.

    Parameters
    ----------
    sines_parameters : ndarray
        Parameters which describe each sine.
    y_intercept : float
        The place where the function is hooked on the y-axis.
    frequency : float
        A value of the frequeny which phases the lightcurve with.

    Returns
    -------
    function
        The sum of sines with two arguments: x, x0.
        x0 is a shift on the x-axis, i.e. f(x-x0).
    """
    def sines(x, x0):
        y = 0

        for par in sines_parameters:
            y += par[0]*np.sin(2*np.pi*par[1]/frequency*(x - x0) + par[2])

        return y + y_intercept

    return sines

def split_filename(filename):
    """
    Split a filename into a name and en extenstion.

    Parameters
    ----------
    filename : str
        The name of the file.

    Returns
    -------
    tuple
        A tuple: (basename, extension).
    """
    return splitext(basename(filename))

def _draw_phase(phase, magnitude, markersize=4):
    plt.xlabel("Phase")
    plt.ylabel("Brightness [mag]")
    plt.gca().invert_yaxis()
    plt.plot(phase, magnitude, '.', alpha=0.5, markersize=markersize)

def _draw_model(X, Y):
    plt.plot(X, Y, 'r-', alpha=0.7)

def display_plot(phase, magnitude, model=None):
    """
    Display a phased lightcurve.

    Parameters
    ----------
    phase : ndarray
        An array which stores a phase vector.
    magnitude : ndarray
        An array which represents a magnitude vector.
    model : tuple
        X, Y coordinates of the model.
    """
    _draw_phase(phase, magnitude, 6)

    if model != None:
        _draw_model(*model)

    plt.show()

def save_plot(phase, magnitdue, filename, model=None):
    """
    Save a phased lightcurve to the file.

    Parameters
    ----------
    phase : ndarray
        An array which stores a phase vector.
    magnitude : ndarray
        An array which represents a magnitude vector.
    filename : str
        The name of a file which will store a phased lightcurve.
    model : tuple
        X, Y coordinates of the model.
    """
    figure = plt.figure(figsize=(10, 5), dpi=150)
    figure.add_subplot(111)
    _draw_phase(phase, magnitude)

    if model != None:
        _draw_model(*model)

    png_filename = join(dirname(filename), split_filename(filename)[0] + ".png")
    figure.savefig(png_filename)


if __name__ == "__main__":
    argparser = ArgumentParser(
        prog='phase.py',
        description='>> Phase a lightcurve <<',
        epilog='Copyright (c) 2018 Przemysław Bruś',
        formatter_class=RawTextHelpFormatter
    )

    argparser.add_argument(
        'lightcurve',
        help=dedent('''\
        The name of a file which stores lightcurve data.
        ------------------------------------
        The file must contain three columns:
        time magnitude magnitude_error

        ''')
    )

    argparser.add_argument(
        'frequency',
        help=dedent('''\
        A value of frequency which phases the lightcurve with.

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

    if args.display:
        display_plot(phase, magnitude, model)

    if args.image:
        save_plot(phase, magnitude, args.lightcurve, model)
