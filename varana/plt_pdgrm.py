"""
Display or save to a file a periodogram.

"""
import matplotlib.pyplot as plt
from numpy import genfromtxt
from re import search


def get_data(filename):
    """
    Get data from a file with two columns.

    Parameters
    ----------
    filename : str
        A name of the input file with data.

    Returns
    -------
    tuple
        A tuple with two ndarrays. Each element stores one column of
        the input file.
    """
    x, y = genfromtxt(filename, unpack=True)

    return x, y


def _draw_periodogram(frequency, amplitude):
    plt.xlabel("Frequency [c/d]")
    plt.ylabel("Amplitude [mag]")
    plt.plot(frequency, amplitude, '-')


def display_periodogram(frequency, amplitude):
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


def save_periodogram(frequency, amplitude, filename):
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

    if search(r'[.]png$', filename):
        png_filename = filename
    else:
        png_filename = filename + ".png"

    figure.savefig(png_filename)
