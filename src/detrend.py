#!/usr/bin/env python3

import matplotlib.pyplot as plt
from numpy import genfromtxt, arange, std, delete, where, stack, savetxt
from scipy.interpolate import InterpolatedUnivariateSpline as spline
from sklearn.cluster import KMeans
from copy import deepcopy
from os.path import basename, splitext, dirname, join
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from textwrap import dedent


def valid_seasons_amount(seasons_amount):
    """
    Check whether the number of seasons is sufficient to detrend the data.

    Parameters
    ----------
    seasons_amount : int
        The number of seasons.

    Returns
    -------
    seasons_amount : int
        The number of seasons or raise the exception.
    """
    if seasons_amount < 2:
        raise ArgumentTypeError("At least 2 seasons in data are required!")
    else:
        return seasons_amount

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

def sigma_clipping_magnitude(data):
    """
    Filter the second column in the data array. Calculate a mean value (m),
    a standard deviation (s) and reject points with values: m +/- 3s.

    Parameters
    ----------
    data : ndarray
        An ndarray with (n, 3)-shape.

    Returns
    -------
    updated_data : ndarray
        The ndarray without clipped points in the second column.
    """
    updated_data = delete(
        data, where((data[:,1] < data[:,1].mean() - 3*std(data[:,1])) |
                    (data[:,1] > data[:,1].mean() + 3*std(data[:,1]))),
        axis=0)

    return updated_data

def too_much_points_rejected(all_points_number, current_points_number):
    """
    Check whether the percentage ratio of size of two sets is to high.

    Parameters
    ----------
    all_points_number : int
        The set which contains all points.
    current_points_number : int
        The set which is smaller or equal than all_points_number.

    Returns
    -------
    True or False
        If the ratio is too high it returns True. Otherwise it returns False.
    """
    if (1 - current_points_number/all_points_number) > 0.05:
        return True
    else:
        return False

def warn_rejected_points(filename):
    """
    Print a warning for the file.

    Parameters
    ----------
    filename : str
        The name of the file to which the warning is concerned.
    """
    print("Rejected too many points from {0:s}".format(filename))

def unpack_data(data):
    """
    Unpack data to the tuple.

    Parameters
    ----------
    data : ndarray
        An ndarray with (n, 3)-shape.

    Returns
    -------
    tuple
        A tuple made of three (n, 1)-shaped ndarrays.
    """
    return data[:,0], data[:,1], data[:,2]

def calculate_kmeans(time, magnitude, error_magnitude, clusters_number=2):
    """
    Calculate a KMeans object.

    Parameters
    ----------
    time : ndarray
        An ndarray which stores float values of time.
    magnitude : ndarray
        An ndarray which stores float values of magnitude.
    error_magnitude : ndarray
        An ndarray which stores float values of magnitude's error.
    clusters_number : int
        The amount of the clusters in the data set (time, magnitude).
        Default = 2.

    Returns
    -------
    KMeans
        The KMeans object.
    """
    kmeans = KMeans(n_clusters=clusters_number,
                    random_state=0).fit(stack((time, magnitude), axis=1),
                                        sample_weight=error_magnitude)

    return kmeans

def sorted_centers(kmeans):
    """
    Sort centers by the first coordinate in the KMeans object.

    Parameters
    ----------
    kmeans : KMeans
        The KMeans object.

    Returns
    -------
    ndarray
        Sorted values in KMeans.cluster_centers_ by the first column.
    """
    return kmeans.cluster_centers_[kmeans.cluster_centers_[:,0].argsort()]

def spline_order(seasons_amount):
    """
    Calculate an order of the spline function. The order must be: 1 <= k <= 5
    and depents on the input parameter.

    Parameters
    ----------
    seasons_amount : int
        The number of seasons in the data.

    Returns
    -------
    int
        The order of the spline function.
    """
    if seasons_amount < 4:
        return seasons_amount - 1
    else:
        return 3

def spline_function(points, order=3):
    """
    Determine a spline function for given points.

    Parameters
    ----------
    points : ndarray
        The (n, 2)-shaped ndarray with points positions.
    order : int
        The order of the final spline function.
        Default = 3.

    Returns
    -------
    function
        The spline function fitted to the points.
    """
    return spline(points[:,0], points[:,1], k=order)

def x_domain_spline(time):
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

def y_domain_spline(spline_function, x_domain_spline):
    """
    Calculate a y domain based on a function.

    Parameters
    ----------
    spline_function : function
        The spline function.
    x_domain_spline : ndarray
        The (n, 1)-shaped ndarray.

    Returns
    -------
    ndarray
        The spline_function(x_domain_spline) vector.
    """
    return spline_function(x_domain_spline)

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

def _draw_plot(time, magnitude, error_magnitude, spline_coordinates, centers):
    x_spline, y_spline = spline_coordinates

    plt.xlabel("Time [JD]")
    plt.ylabel("Brightness [mag]")
    plt.plot(x_spline, len(x_spline)*[magnitude.mean()],
             color="gray", linewidth=0.8, linestyle="dashed")
    plt.plot(time, magnitude, '.', alpha=0.8)
    plt.plot(x_spline, y_spline, 'r--')
    for center in centers:
        plt.plot(center[0], center[1], 'r.', markersize=15)

def display_plot(time, magnitude, error_magnitude, spline_coordinates, centers):
    """
    Display a plot.

    Parameters
    ----------
    time : ndarray
        The time vector.
    magnitude : ndarray
        The magnitude vector.
    error_magnitude : ndarray
        The error of magnitude vector.
    spline_coordinates : ndarray
        The (n, 2)-shaped ndarray with points.
    centers : ndarray
        The (n, 2)-shaped ndarray with points.
    """
    _draw_plot(time, magnitude, error_magnitude, spline_coordinates, centers)
    plt.show()

def save_plot(time, magnitude, error_magnitude,
              spline_coordinates, centers, filename):
    """
    Save a plot to a file.

    Parameters
    ----------
    time : ndarray
        The time vector.
    magnitude : ndarray
        The magnitude vector.
    error_magnitude : ndarray
        The error of magnitude vector.
    spline_coordinates : ndarray
        The (n, 2)-shaped ndarray with points.
    centers : ndarray
        The (n, 2)-shaped ndarray with points.
    filename : str
        The name of a PNG file to which to save a plot.
    """
    figure = plt.figure(figsize=(10, 5), dpi=150)
    figure.add_subplot(111)
    _draw_plot(time, magnitude, error_magnitude, spline_coordinates, centers)
    png_filename = join(dirname(filename), split_filename(filename)[0] + ".png")
    figure.savefig(png_filename)

def detrend_data(data, spline, mean_magnitude):
    """
    Detrend magnitudes from the data using a spline function.

    Parameters
    ----------
    data : ndarray
        An object which stores the data in three columns:
        time magnitude error_magnitude
    spline : function
        A spline function.
    mean_magnitude : float
        A value of mean magnitudes from the data (without outstanding points).

    Returns
    -------
    data : ndarray
        Updated data.
    """
    data[:,1] = data[:,1] - spline(data[:,0]) + mean_magnitude
    return data


if __name__ == "__main__":
    argparser = ArgumentParser(
        prog='detrend.py',
        description='>> Removes seasonal trends from a lightcurve <<',
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
        The name of a file which will store a detrended lightcurve.

        ''')
    )

    argparser.add_argument(
        'seasons_amount',
        help=dedent('''\
        The number of seasons in the data.
        The seasons are separated by time-gaps in the data.

        '''),
        type=int
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
        display_plot(time, magnitude, error_magnitude,
                     spline_coordinates, centers)
    if args.image:
        save_plot(time, magnitude, error_magnitude, spline_coordinates,
                  centers, args.output_lightcurve)

    detrended_data = detrend_data(org_data, spline, magnitude.mean())
    savetxt(args.output_lightcurve, detrended_data, fmt="%16.6f %9.4f %7.4f")
