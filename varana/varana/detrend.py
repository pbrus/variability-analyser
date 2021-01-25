"""
Detrend a light curve removing seasonal deviations.

"""
from os.path import basename, splitext, dirname, join
from pathlib import Path
from typing import Callable, Tuple

import matplotlib.pyplot as plt
from astropy.stats import sigma_clip
from numpy import genfromtxt, ndarray, linspace, where, logical_and, mean, isnan, full, nan
from scipy.interpolate import Akima1DInterpolator


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


def sigma_clipping_magnitude(
    data: Tuple[ndarray, ndarray, ndarray], sigma: float = 3.0
) -> Tuple[ndarray, ndarray, ndarray]:
    """
    Filter the data using 3x sigma clipping of magnitudes.

    Parameters
    ----------
    data : Tuple[ndarray, ndarray, ndarray]
        A tuple consisting of three (n, 1)-shape arrays.
    sigma : float
        The number of standard deviations. Default is 3.0.

    Returns
    -------
    Tuple[ndarray, ndarray, ndarray]
        Updated data with removed outstanding points of magnitude.

    """
    mask = ~sigma_clip(data[1], sigma=sigma).mask
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


def _calculate_intervals_for_nodes(start: float, stop: float, nodes_number: int) -> ndarray:
    """For a given number of nodes and time range determine equal intervals for a time series."""
    return linspace(start, stop, num=(nodes_number + 1))


def calculate_nodes_positions(time: ndarray, magnitude: ndarray, nodes_number: int) -> ndarray:
    """
    Calculate positions of nodes for interpolation.

    Parameters
    ----------
    time : ndarray
        (n, 1)-shaped array representing time.
    magnitude : ndarray
        (n, 1)-shaped array representing brightness.
    nodes_number : int
        A number of nodes (m) for a curve fitting.

    Returns
    -------
    positions : ndarray
        (m, 2)-shaped array storing positions of the nodes.

    """
    positions = full((nodes_number, 2), nan)
    start, stop = min(time), max(time)
    intervals = _calculate_intervals_for_nodes(start, stop, nodes_number)

    for i, (beg, end) in enumerate(zip(intervals, intervals[1:])):
        if i < nodes_number - 1:
            indices, *_ = where(logical_and(time >= beg, time < end))
        else:
            indices, *_ = where(logical_and(time >= beg, time <= end))

        if indices.size == 0:
            continue

        positions[i] = [mean(time[indices]), mean(magnitude[indices])]

    return positions[~isnan(positions)].reshape(-1, 2)


def akima(nodes_positions: ndarray) -> Akima1DInterpolator:
    """
    A wrapper function for Akima's interpolation.

    Parameters
    ----------
    nodes_positions : ndarray
        (m, 2)-shaped array storing positions of the nodes.

    Returns
    -------
    Akima1DInterpolator
        Piecewise cubic polynomials described by Akima.

    """
    function = Akima1DInterpolator(nodes_positions[:, 0], nodes_positions[:, 1])
    function.extrapolate = True
    return function


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
    time: ndarray, magnitude: ndarray, function: Callable, nodes_positions: ndarray, marker_size: int = 2
) -> None:
    plt.xlabel("Time")
    plt.ylabel("Brightness [mag]")
    plt.gca().invert_yaxis()
    plt.plot(time, len(time) * [magnitude.mean()], color="gray", linewidth=0.8, linestyle="dashed")
    plt.plot(time, magnitude, ".", alpha=0.8, markersize=marker_size)
    plt.plot(time, function(time), "r--", linewidth=1.2)
    plt.plot(nodes_positions[:, 0], nodes_positions[:, 1], "r.", markersize=10)


def display_plot(time: ndarray, magnitude: ndarray, function: Callable, nodes_positions: ndarray) -> None:
    """
    Display a plot.

    Parameters
    ----------
    time : ndarray
        The time vector.
    magnitude : ndarray
        The magnitude vector.
    function : Callable
        Interpolation function.
    nodes_positions : ndarray
        (m, 2)-shaped array storing positions of the nodes.

    """
    _draw_plot(time, magnitude, function, nodes_positions, 4)
    plt.show()


def save_plot(time: ndarray, magnitude: ndarray, function: Callable, nodes_positions: ndarray, filename: str) -> None:
    """
    Save a plot to a file.

    Parameters
    ----------
    time : ndarray
        The time vector.
    magnitude : ndarray
        The magnitude vector.
    function : Callable
        Interpolation function.
    nodes_positions : ndarray
    filename : str
        The name of a PNG file to which to save a plot.

    """
    figure = plt.figure(figsize=(10, 5), dpi=150)
    figure.add_subplot(111)
    _draw_plot(time, magnitude, function, nodes_positions)
    png_filename = join(dirname(filename), split_filename(filename)[0] + ".png")
    figure.savefig(png_filename)


def detrend_magnitude(time: ndarray, magnitude: ndarray, function: Callable, mean_magnitude: float = 0.0) -> ndarray:
    """
    Detrend magnitudes from the data using an interpolated function.

    Parameters
    ----------
    time : ndarray
        The time vector.
    magnitude : ndarray
        The magnitude vector.
    function : Callable
        Interpolation function.
    mean_magnitude : float
        A mean value of magnitude.

    Returns
    -------
    magnitude : ndarray
        The magnitude vector without trend.

    """
    return magnitude - function(time) + mean_magnitude
