#!/usr/bin/env python3

import matplotlib.pyplot as plt
from numpy import genfromtxt, arange, std, delete, where, stack
from scipy.interpolate import InterpolatedUnivariateSpline as spline
from sklearn.cluster import KMeans
from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent


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

def calculate_kmeans(time, magnitude, error_magnitude, clusters_number=9):
    kmeans = KMeans(n_clusters=clusters_number,
                    random_state=0).fit(stack((time, magnitude), axis=1),
                                        sample_weight=error_magnitude)

    return kmeans

def sorted_centers(kmeans):
    return kmeans.cluster_centers_[kmeans.cluster_centers_[:,0].argsort()]

def spline_function(clusters_centers, order=3):
    return spline(clusters_centers[:,0], clusters_centers[:,1], k=order)

def x_domain_spline(time):
    return arange(time.min(), time.max(), (time.max() - time.min())/len(time))

def y_domain_spline(x_domain_spline):
    return spline_function(x_domain_spline)


if __name__ == "__main__":
    argparser = ArgumentParser(
        prog='detrend.py',
        description='>> Removes trends from a lightcurve <<',
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

    args = argparser.parse_args()
    data = get_data(args.input_lightcurve)
    all_points_number = len(data)
    data = sigma_clipping_magnitude(data)

    if too_much_points_rejected(all_points_number, len(data)):
        warn_rejected_points(args.input_lightcurve)

    time, magnitude, error_magnitude = unpack_data(data)
    kmeans = calculate_kmeans(time, magnitude, error_magnitude)
    centers = sorted_centers(kmeans)
    spline = spline_function(centers)
    x_spline = x_domain_spline(time)
    y_spline = spline(x_spline)

    plt.xlabel("Time [JD]")
    plt.ylabel("Brightness [mag]")
    plt.plot(x_spline, len(x_spline)*[magnitude.mean()],
             color="gray", linewidth=0.8, linestyle="dashed")
    #plt.plot(time, magnitude - spline_function(time) + mean_magnitude, '.')
    plt.plot(time, magnitude, '.', alpha=0.8)
    plt.plot(x_spline, y_spline, 'r--')
    for center in centers:
        plt.plot(center[0], center[1], 'r.', markersize=15)
    plt.show()
