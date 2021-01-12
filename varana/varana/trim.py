#!/usr/bin/env python3
"""
Trim a light curve using the sigma clipping or a manual rejection.

"""
from argparse import ArgumentParser, RawTextHelpFormatter
from copy import deepcopy
from os.path import dirname, join
from textwrap import dedent

import matplotlib.pyplot as plt
import numpy.ma as ma
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
from matplotlib.widgets import Cursor
from numpy import genfromtxt, std, arange, savetxt, bool_, ndarray, array_equal
from numpy.ma import masked_array

from varana.detrend import split_filename

limit = list()
lim = list()


def get_data(filename: str) -> ndarray:
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


def trim(data: ndarray, lower_cut: float = 0.0, upper_cut: float = 0.0) -> masked_array:
    """
    Trim the second column of the data. If lower_cut and upper_cut are both equal 0.0 then the trim will base on 3s.

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
    if lower_cut == 0.0 and upper_cut == 0.0:
        trimmed_data = sigma_clipping(data)
    else:
        trimmed_data = cutoff(data, lower_cut, upper_cut)

    return trimmed_data


def sigma_clipping(data: ndarray) -> masked_array:
    """
    Filter the second column in the data array. Calculate a mean value (m), a standard deviation (s) and reject points
    with values: m +/- 3s.

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
        masked_data[:, i] = ma.masked_where(
            (data[:, 1] < data[:, 1].mean() - 3 * std(data[:, 1]))
            | (data[:, 1] > data[:, 1].mean() + 3 * std(data[:, 1])),
            data[:, i],
        )

    return masked_data


def cutoff(data: ndarray, lower_cut: float, upper_cut: float) -> masked_array:
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
    masked_data.mask = False

    for i in range(masked_data.shape[1]):
        masked_data[:, i] = ma.masked_where((data[:, 1] < lower_cut) | (data[:, 1] > upper_cut), data[:, i])

    return masked_data


def x_domain(time: ndarray) -> ndarray:
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
    t = deepcopy(time)
    t.mask = False

    return arange(t.min(), t.max(), (t.max() - t.min()) / len(t))


def _draw_plot(ax: Axes, data: masked_array, lower_line: int, upper_line: int, marker_size: int = 2) -> None:
    ax.set_xlabel("Time")
    ax.set_ylabel("Brightness [mag]")
    ax.invert_yaxis()

    if not (lower_line == 0 and upper_line == 0):
        ax.plot(
            x_domain(data[:, 0]),
            [lower_line] * len(x_domain(data[:, 0])),
            color="gray",
            linewidth=0.8,
            linestyle="dashed",
        )
        ax.plot(
            x_domain(data[:, 0]),
            [upper_line] * len(x_domain(data[:, 0])),
            color="gray",
            linewidth=0.8,
            linestyle="dashed",
        )

    ax.plot(data[:, 0], data[:, 1], ".", markersize=marker_size)
    data.mask = ~data.mask
    ax.plot(data[:, 0], data[:, 1], "r.", markersize=marker_size)
    data.mask = ~data.mask


def display_plot(ax: Axes, data: masked_array, lower_line: int, upper_line: int) -> None:
    """
    Display an interactive plot. Mark lower and upper limit of magnitude by clicking on the plot.

    Parameters
    ----------
    ax : AxesSubplot
        An axes subplot.
    data : MaskedArray
        The (n, 3)-shaped array with data.
    lower_line : float
        A bottom cut-off for magnitude.
    upper_line : float
        An upper cut-off for magnitude.

    """
    ax.cla()
    _draw_plot(ax, data, lower_line, upper_line, 4)
    _ = Cursor(ax, useblit=True, color="gray", linewidth=0.5)
    fig.canvas.mpl_connect("button_press_event", _onclick)
    plt.show()


def _onclick(event: MouseEvent) -> None:
    global limit, lim
    limit.append(event.ydata)

    if len(limit) == 2:
        if len(set(limit)) == 1:
            limit = list()
        else:
            lim = sorted(deepcopy(limit))
            limit = list()
            display_plot(axs, cutoff(input_data, lim[0], lim[1]), lim[0], lim[1])


def save_plot(data: masked_array, filename: str, lower_line: int = 0, upper_line: int = 0) -> None:
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
    ax = figure.add_subplot(111)
    _draw_plot(ax, data, lower_line, upper_line)
    png_filename = join(dirname(filename), split_filename(filename)[0] + ".png")
    figure.savefig(png_filename)


def filter_lightcurve(data: ndarray, trim_data: masked_array) -> ndarray:
    """
    Filter the data removing outstanding points, i.e. masked rows.

    Parameters
    ----------
    data : ndarray
        The (n, 3)-shaped array with data to clip.
    trim_data : MaskedArray
        The (n, 3)-shaped array with masked points.

    Returns
    -------
    ndarray
        The (n, 3)-shaped array without outstanding points.

    """
    if not array_equal(data[:, 0], trim_data.data[:, 0]):
        raise ValueError("Cannot trim light curve. Got different data")

    data = ma.array(data, mask=trim_data.mask)

    if type(data.mask) == bool_:
        return data
    else:
        n = data.shape[0] - len([row for row in data.mask if row.all()])
        m = data.shape[1]
        return data.data[~data.mask].reshape(n, m)


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        prog="trim.py",
        description=">> Removes outstanding points from a light curve <<",
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
        The name of a file which will store a filtered light curve.

        """
        ),
    )

    arg_parser.add_argument(
        "--min",
        help=dedent(
            """\
        The minimum value of magnitude.

        """
        ),
        dest="min",
        type=float,
        default=0.0,
    )

    arg_parser.add_argument(
        "--max",
        help=dedent(
            """\
        The maximum value of magnitude.

        """
        ),
        dest="max",
        type=float,
        default=0.0,
    )

    arg_parser.add_argument(
        "--lightcurve",
        help=dedent(
            """\
        The name of a file which will store an additional
        light curve which should be also clipped.

        """
        ),
        metavar="filename",
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
    input_data = None

    try:
        input_data = get_data(args.input_lightcurve)
    except OSError as error:
        print(error)
        exit()

    trim_data = trim(input_data, args.min, args.max)

    if args.display:
        fig = plt.figure()
        axs = fig.add_subplot(111)
        display_plot(axs, trim_data, args.min, args.max)
        if lim:
            trim_data = trim(trim_data, lim[0], lim[1])

    if args.image:
        if args.display and lim != []:
            trim_data = trim(trim_data, lim[0], lim[1])
            save_plot(trim_data, args.output_lightcurve, lim[0], lim[1])
        else:
            save_plot(trim_data, args.output_lightcurve, args.min, args.max)

    savetxt(args.output_lightcurve, filter_lightcurve(input_data, trim_data), fmt="%18.7f %15.7f %15.7f")

    if args.lightcurve:
        data = get_data(args.lightcurve)
        savetxt(args.lightcurve, filter_lightcurve(data, trim_data), fmt="%18.7f %15.7f %15.7f")
