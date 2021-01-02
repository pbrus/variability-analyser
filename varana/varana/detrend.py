"""
Detrend a light curve removing seasonal deviations.

"""
from os.path import basename, splitext, dirname, join
from pathlib import Path
from typing import Callable, Tuple

import matplotlib.pyplot as plt
from astropy.stats import sigma_clip
from numpy import genfromtxt, arange, stack, ceil, floor
from numpy import ndarray
from scipy.interpolate import InterpolatedUnivariateSpline as Spline
from sklearn.cluster import KMeans


def load_data(filename: str) -> Tuple[ndarray, ndarray, ndarray]:
    """
    Load the data from a text file to separate arrays.

    Parameters
    ----------
    filename : str
        A name of a file with data. The file should contain three n-element columns:
         - time
         - brightness
         - error of brightness

        All data should be represented by floats.

    Returns
    -------
    tuple
        A tuple made of three (n, 1)-shaped ndarrays.

    """
    data = genfromtxt(Path(filename))
    return data[:, 0], data[:, 1], data[:, 2]


def validate_nodes_number(nodes_number: int) -> int:
    """
    Check whether a number of nodes is sufficient to detrend the data.

    Parameters
    ----------
    nodes_number : int
        The number of nodes.

    Returns
    -------
    int
        The number of nodes.

    Raises
    ------
    ValueError
        Raise when the number of nodes is not sufficient.

    """
    min_nodes_number = 2

    if nodes_number < min_nodes_number:
        raise ValueError(f"At least {min_nodes_number} nodes are required to detrend data")
    else:
        return nodes_number


def set_interval(start: float, stop: float, nodes_number: int) -> float:
    """
    Determine an interval of a time series for a given number of nodes.

    Parameters
    ----------
    start : float
        The beginning of the time series.
    stop : float
        The end of the time series.
    nodes_number : int
        The number of nodes which divide the time series into chunks.

    Returns
    -------
    float
        A length of a time interval.

    """
    return (ceil(stop) - floor(start)) / nodes_number


def sigma_clipping_magnitude(data: Tuple[ndarray, ndarray, ndarray]) -> Tuple[ndarray, ndarray, ndarray]:
    """
    Filter the data using 3x sigma clipping of magnitudes.

    Parameters
    ----------
    data : Tuple[ndarray, ndarray, ndarray]
        A tuple consisting of three (n, 1)-shape arrays.

    Returns
    -------
    Tuple[ndarray, ndarray, ndarray]
        Updated data with removed outstanding points of magnitude.

    """
    mask = ~sigma_clip(data[1], sigma=3.0).mask
    return data[0][mask], data[1][mask], data[2][mask]


def too_many_points_rejected(filename: str, all_points_number: int, current_points_number: int) -> None:
    """
    For a given data check whether the sigma clipping did reject too many points, i.e. more than 5%.

    Parameters
    ----------
    filename : str
        A name of the file storing the data.
    all_points_number : int
        The set which contains all points.
    current_points_number : int
        The set which is smaller or equal than all_points_number.

    Raises
    ------
    ValueError
        Raise when rejected points is more than 5%.

    """
    if (1 - current_points_number / all_points_number) > 0.05:
        raise ValueError(f"Rejected too many points from {filename}")


def calculate_kmeans(time: ndarray, magnitude: ndarray, error_magnitude: ndarray, clusters_number: int = 2) -> KMeans:
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
    kmeans = KMeans(n_clusters=clusters_number, random_state=0).fit(
        stack((time, magnitude), axis=1), sample_weight=error_magnitude
    )

    return kmeans


def sorted_centers(kmeans: KMeans) -> ndarray:
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
    return kmeans.cluster_centers_[kmeans.cluster_centers_[:, 0].argsort()]


def spline_order(seasons_amount: int) -> int:
    """
    Calculate an order of the spline function. The order must be: 1 <= k <= 5 and depends on the input parameter.

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


def spline_function(points: ndarray, order: int = 3) -> Callable:
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
    return Spline(points[:, 0], points[:, 1], k=order)


def x_domain_spline(time: ndarray) -> ndarray:
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
    return arange(time.min(), time.max(), (time.max() - time.min()) / len(time))


def y_domain_spline(spline_func: Callable, x_domain: ndarray) -> ndarray:
    """
    Calculate a y domain based on a function.

    Parameters
    ----------
    spline_func : function
        The spline function.
    x_domain : ndarray
        The (n, 1)-shaped ndarray.

    Returns
    -------
    ndarray
        The spline_function(x_domain_spline) vector.

    """
    return spline_func(x_domain)


def split_filename(filename: str) -> Tuple[str, str]:
    """
    Split a filename into a name and an extension.

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


def _draw_plot(
    time: ndarray, magnitude: ndarray, spline_coordinates: tuple, centers: ndarray, marker_size: int = 2
) -> None:
    x_spline, y_spline = spline_coordinates

    plt.xlabel("Time")
    plt.ylabel("Brightness [mag]")
    plt.gca().invert_yaxis()
    plt.plot(x_spline, len(x_spline) * [magnitude.mean()], color="gray", linewidth=0.8, linestyle="dashed")
    plt.plot(time, magnitude, ".", alpha=0.8, markersize=marker_size)
    plt.plot(x_spline, y_spline, "r--", linewidth=1.5)
    for center in centers:
        plt.plot(center[0], center[1], "r.", markersize=15)


def display_plot(time: ndarray, magnitude: ndarray, spline_coordinates: tuple, centers: ndarray) -> None:
    """
    Display a plot.

    Parameters
    ----------
    time : ndarray
        The time vector.
    magnitude : ndarray
        The magnitude vector.
    spline_coordinates : tuple
        The tuple containing two arrays (ndarray) with coordinates.
    centers : ndarray
        The (n, 2)-shaped ndarray with points.

    """
    _draw_plot(time, magnitude, spline_coordinates, centers, 4)
    plt.show()


def save_plot(time: ndarray, magnitude: ndarray, spline_coordinates: tuple, centers: ndarray, filename: str) -> None:
    """
    Save a plot to a file.

    Parameters
    ----------
    time : ndarray
        The time vector.
    magnitude : ndarray
        The magnitude vector.
    spline_coordinates : ndarray
        The tuple containing two arrays (ndarray) with coordinates.
    centers : ndarray
        The (n, 2)-shaped ndarray with points.
    filename : str
        The name of a PNG file to which to save a plot.

    """
    figure = plt.figure(figsize=(10, 5), dpi=150)
    figure.add_subplot(111)
    _draw_plot(time, magnitude, spline_coordinates, centers)
    png_filename = join(dirname(filename), split_filename(filename)[0] + ".png")
    figure.savefig(png_filename)


def detrend_data(data: ndarray, spline_func: Callable, mean_magnitude: float):
    """
    Detrend magnitudes from the data using a spline function.

    Parameters
    ----------
    data : ndarray
        An object which stores the data in three columns:
        time magnitude error_magnitude
    spline_func : function
        A spline function.
    mean_magnitude : float
        A value of mean magnitudes from the data (without outstanding points).

    Returns
    -------
    data : ndarray
        Updated data.

    """
    data[:, 1] = data[:, 1] - spline_func(data[:, 0]) + mean_magnitude
    return data
