#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy.ma as ma
from numpy import genfromtxt, std, arange, savetxt
from copy import deepcopy
from os.path import basename, splitext, dirname, join
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from textwrap import dedent


def get_data(filename):
    """
    Alias for the numpy.genfromtxt function.

    Parameters
    ----------
    filename : str
        The name of a file with data.

    Returns
    -------
    ndarray
        The data from the input file stored in an ndarray object.
    """
    return genfromtxt(filename)

def trim(data, lower_cut=0, upper_cut=0):
    """
    Trim the second column of the data. If lower_cut and upper_cut are both
    equal 0, then the trim bases on 3 x sigma clipping.

    Parameters
    ----------
    data : ndarray
        The ndarray without clipped points in the second column.
    lower_cut : float
        A bottom cut-off for data in the second column.
        Default = 0.
    upper_cut : float
        An upper cut-off for data in the second column.
        Default = 0.

    Returns
    -------
    masked_data : MaskedArray
        The ndarray with masked outstanding points in the second column.
    """
    if (lower_cut == 0 and upper_cut == 0):
        trim_data = sigma_clipping(data)
    else:
        trim_data = cutoff(data, lower_cut, upper_cut)

    return trim_data

def sigma_clipping(data):
    """
    Filter the second column in the data array. Calculate a mean value (m),
    a standard deviation (s) and reject points with values: m +/- 3s.

    Parameters
    ----------
    data : ndarray
        An ndarray with (n, 3)-shape.

    Returns
    -------
    masked_data : MaskedArray
        The ndarray with masked clipped-points in the second column.
    """
    masked_data = ma.masked_array(data)

    for i in range(masked_data.shape[1]):
        masked_data[:,i] = ma.masked_where(
            (data[:,1] < data[:,1].mean() - 3*std(data[:,1])) |
            (data[:,1] > data[:,1].mean() + 3*std(data[:,1])), data[:,i])

    return masked_data

def cutoff(data, lower_cut, upper_cut):
    """
    Cut-off the values in the second column of data array.

    Parameters
    ----------
    data : ndarray
        An ndarray with (n, 3)-shape.
    lower_cut : float
        A bottom cut-off for data in the second column.
    upper_cut : float
        An upper cut-off for data in the second column.

    Returns
    -------
    masked_data : MaskedArray
        The ndarray with masked clipped-points in the second column.
    """
    masked_data = ma.masked_array(data)

    for i in range(masked_data.shape[1]):
        masked_data[:,i] = ma.masked_where(
            (data[:,1] < lower_cut) | (data[:,1] > upper_cut), data[:,i])

    return masked_data

def x_domain(time):
    """
    Define an x domain for time vector that its points are equal separated.

    Parameters
    ----------
    time : ndarray
        The (n, 1)-shaped ndarray.

    Returns
    -------
    ndarray
        The transformed time vector.
    """
    return arange(time.min(), time.max(), (time.max() - time.min())/len(time))

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

def _draw_plot(data, lower_line, upper_line):
    plt.xlabel("Time [JD]")
    plt.ylabel("Brightness [mag]")

    if not (lower_line == 0 and upper_line == 0):
        plt.plot(x_domain(data[:,0]), [lower_line]*len(x_domain(data[:,0])),
                 color="gray", linewidth=0.8, linestyle="dashed")
        plt.plot(x_domain(data[:,0]), [upper_line]*len(x_domain(data[:,0])),
                 color="gray", linewidth=0.8, linestyle="dashed")

    plt.plot(data[:,0], data[:,1], '.')
    data.mask = ~data.mask
    plt.plot(data[:,0], data[:,1], 'r.')

def display_plot(data, lower_line, upper_line):
    """
    Display a plot.

    Parameters
    ----------
    data : MaskedArray
        The (n, 3)-shaped array with data.
    lower_line : float
        A bottom cut-off for magnitude.
    upper_line : float
        An upper cut-off for magnitude.
    """
    _draw_plot(data, lower_line, upper_line)
    plt.show()

def save_plot(data, filename, lower_line=0, upper_line=0):
    """
    Save a plot to a file.

    Parameters
    ----------
    data : MaskedArray
        The (n, 3)-shaped array with data.
    filename : str
        The name of a PNG file to which to save a plot.
    lower_line : float
        A bottom cut-off for magnitude.
    upper_line : float
        An upper cut-off for magnitude.
    """
    figure = plt.figure(figsize=(10, 5), dpi=150)
    figure.add_subplot(111)
    _draw_plot(data, lower_line, upper_line)
    png_filename = join(dirname(filename), split_filename(filename)[0] + ".png")
    figure.savefig(png_filename)

def filter_lightcurve(data):
    """
    Filter the data removing outstanding points, i.e. masked rows.

    Parameters
    ----------
    data : MaskedArray
        The (n, 3)-shaped array with data.

    Returns
    -------
    ndarray
        The (n, 3)-shaped array without outstanding points.
    """
    n = data.shape[0] - len([row for row in data.mask if row.all()])
    m = data.shape[1]

    return data.data[~data.mask].reshape(n, m)


if __name__ == "__main__":
    argparser = ArgumentParser(
        prog='trim.py',
        description='>> Removes outstanding points from a lightcurve <<',
        epilog='Copyright (c) 2018 Przemysław Bruś',
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
    trim_data_copy = deepcopy(trim_data)

    if args.display:
        display_plot(trim_data, args.min, args.max)

    if args.image:
        save_plot(trim_data_copy, args.output_lightcurve, args.min, args.max)

    savetxt(args.output_lightcurve, filter_lightcurve(trim_data),
            fmt="%16.6f %9.4f %7.4f")
