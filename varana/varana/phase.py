"""
Phase a light curve with a specific frequency.

"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from copy import deepcopy
from warnings import filterwarnings
from os.path import basename, splitext, dirname, join

filterwarnings("ignore",
               message="Covariance of the parameters could not be estimated")


def read_lightcurve(filename):
    """
    Read a light curve from a file.

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
        A value of period which phases the light curve with.

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
    Phase a light curve with the frequency.

    Parameters
    ----------
    filename : str
        A name of a file which stores a light curve.
    frequency : float
        A value of the frequeny which phases the light curve with.
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
    Get a model in XY coordinates and align it to the phased light curve.

    Parameters
    ----------
    filename : str
        A name of a file which stores a model.
    frequency : float
        A value of the frequeny which phases the light curve with.
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
    min_phase, max_phase = int(round(phase.min())), int(round(phase.max()))
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
        A value of the frequeny which phases the light curve with.

    Returns
    -------
    function
        The sum of sines with two arguments: x, x0.
        x0 is a shift on the x-axis, i.e. f(x-x0).
    """
    def sines(x, x0):
        y = 0

        for par in sines_parameters.reshape(-1, 3):
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
    Display a phased light curve.

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

    if model is not None:
        _draw_model(*model)

    plt.show()


def save_plot(phase, magnitude, filename, model=None):
    """
    Save an image with a phased light curve to the file.

    Parameters
    ----------
    phase : ndarray
        An array which stores a phase vector.
    magnitude : ndarray
        An array which represents a magnitude vector.
    filename : str
        The name of a file which will store the image of a phased light curve.
    model : tuple
        X, Y coordinates of the model.
    """
    figure = plt.figure(figsize=(10, 5), dpi=150)
    figure.add_subplot(111)
    _draw_phase(phase, magnitude)

    if model is not None:
        _draw_model(*model)

    png_filename = join(dirname(filename), split_filename(filename)[0]
                        + ".png")
    figure.savefig(png_filename)


def save_phased_lightcurve(phase, magnitude, filename):
    """
    Save a phased light curve to the file.

    Parameters
    ----------
    phase : ndarray
        An array which stores a phase vector.
    magnitude : ndarray
        An array which represents a magnitude vector.
    filename : str
        The name of a file which will store a phased light curve.
    """
    result = np.append(phase.reshape(1, -1), magnitude.reshape(1, -1), axis=0)
    np.savetxt(filename, result.T, fmt="%16.6f %9.4f")
