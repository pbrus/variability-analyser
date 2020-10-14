"""
Display or save a periodogram to a file.

"""
from re import search

import matplotlib.pyplot as plt
from numpy import genfromtxt, ndarray


def get_data(filename: str) -> ndarray:
    """
    Get data from a file with two columns.

    Parameters
    ----------
    filename : str
        A name of the input file with data.

    Returns
    -------
    ndarray
        Unpacked array which stores data from input file.

    """
    return genfromtxt(filename, unpack=True)


def _draw_periodogram(frequency: ndarray, amplitude: ndarray) -> None:
    plt.xlabel("Frequency [c/d]")
    plt.ylabel("Amplitude [mag]")
    plt.plot(frequency, amplitude, "-")


def display_periodogram(frequency: ndarray, amplitude: ndarray) -> None:
    """
    Display a periodogram.

    Parameters
    ----------
    frequency : ndarray
        An array which represents frequencies.
    amplitude : ndarray
        An array which stores values of amplitude for each frequency.

    """
    _draw_periodogram(frequency, amplitude)
    plt.show()


def save_periodogram(frequency: ndarray, amplitude: ndarray, filename: str) -> None:
    """
    Save a periodogram to the file.

    Parameters
    ----------
    frequency : ndarray
        An array which represents frequencies.
    amplitude : ndarray
        An array which stores values of amplitude for each frequency.
    filename : str
        The name of a PNG file to which to save a plot.

    """
    figure = plt.figure(figsize=(10, 5), dpi=150)
    figure.add_subplot(111)
    _draw_periodogram(frequency, amplitude)

    if search(r"[.]png$", filename):
        png_filename = filename
    else:
        png_filename = filename + ".png"

    figure.savefig(png_filename)
