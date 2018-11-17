#!/usr/bin/env python3

import matplotlib.pyplot as plt
from numpy import genfromtxt, arange, std, delete, where, stack
from scipy.interpolate import InterpolatedUnivariateSpline as spline
from sklearn.cluster import KMeans
from copy import deepcopy
from os.path import basename, splitext, dirname, join
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from textwrap import dedent


def valid_seasons_amount(seasons_amount):
    if seasons_amount < 2:
        raise ArgumentTypeError("At least 2 seasons in data are required!")
    else:
        return seasons_amount

def get_data(filename):
    return genfromtxt(filename)

def sigma_clipping_magnitude(data):
    updated_data = delete(
        data, where((data[:,1] < data[:,1].mean() - 3*std(data[:,1])) |
                    (data[:,1] > data[:,1].mean() + 3*std(data[:,1]))),
        axis=0)

    return updated_data

def too_much_points_rejected(all_points_number, current_points_number):
    if (1 - current_points_number/all_points_number) > 0.05:
        return True

def warn_rejected_points(filename):
    print("Rejected too many points from {0:s}".format(filename))

def unpack_data(data):
    return data[:,0], data[:,1], data[:,2]

def calculate_kmeans(time, magnitude, error_magnitude, clusters_number=2):
    kmeans = KMeans(n_clusters=clusters_number,
                    random_state=0).fit(stack((time, magnitude), axis=1),
                                        sample_weight=error_magnitude)

    return kmeans

def sorted_centers(kmeans):
    return kmeans.cluster_centers_[kmeans.cluster_centers_[:,0].argsort()]

def spline_order(seasons_amount):
    if seasons_amount < 4:
        return seasons_amount - 1
    else:
        return 3

def spline_function(clusters_centers, order=3):
    return spline(clusters_centers[:,0], clusters_centers[:,1], k=order)

def x_domain_spline(time):
    return arange(time.min(), time.max(), (time.max() - time.min())/len(time))

def y_domain_spline(x_domain_spline):
    return spline_function(x_domain_spline)

def split_filename(filename):
    return splitext(basename(filename))

def draw_plot(time, magnitude, error_magnitude, spline_coordinates, centers):
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
    draw_plot(time, magnitude, error_magnitude, spline_coordinates, centers)
    plt.show()

def save_plot(time, magnitude, error_magnitude,
              spline_coordinates, centers, filename):

    draw_plot(time, magnitude, error_magnitude, spline_coordinates, centers)
    png_filename = join(dirname(filename), split_filename(filename)[0] + ".png")
    plt.savefig(png_filename, dpi=150)


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

    #plt.plot(time, magnitude - spline_function(time) + mean_magnitude, '.')

