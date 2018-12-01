#!/usr/bin/env python3

import numpy as np
from scipy.optimize import least_squares


def fit_approximate_sine(frequency):
    """
    A single sine function with a set frequency.

    Parameters
    ----------
    frequency : float
        Frequency of a single sine function.

    Returns
    -------
    function
        f(amp, phase, y0, x) = amp*sin(2*PI*frequency*x + phase) + y0
    """
    def approximate_sine(x, amplitude, phase, y_intercept):
        return amplitude*np.sin(2*np.pi*frequency*x + phase) + y_intercept

    return approximate_sine

def sine_residuals(frequency):
    """
    Define a function determining residuals of a fitted sine to the data on
    the xy plane.

    Parameters
    ----------
    frequency : float
        Frequency of a single sine function.

    Returns
    -------
    function
        f(amp, phase, y0, x, y) = amp*sin(2*PI*frequency*x + phase) + y0 - y
    """
    def residuals(parameters, x, y):
        approximate_sine = fit_approximate_sine(frequency)
        return approximate_sine(x, *parameters) - y

    return residuals

def approximate_sine_parameters(lightcurve, frequency):
    """
    Determine approximate parameters of a sine with set frequency fitting it
    to the data.

    Parameters
    ----------
    lightcurve : ndarray
        An ndarray with (n, 3)-shape storing: time, magnitude, mag's error.
    frequency : float
        Frequency of a single sine function.

    Returns
    -------
    ndarray
        Determined parameters of the sine: amplitude, phase and y_intercept.
    """
    x0 = np.array([0., 0., 0.])
    result = least_squares(sine_residuals(frequency), x0,
                           args=(lightcurve[:,0], lightcurve[:,1]))

    return result.x

def sine(frequency, amplitude, phase, y_intercept):
    """
    A single sine function with set parameters.

    Parameters
    ----------
    frequency : float
        Frequency of the sine function.
    amplitude : float
        Amplitude of the sine function.
    phase : float
        Phase of the sine function.
    y_intercept : float
        Vertical intercept.

    Returns
    -------
    function
        f(x) = amplitude*sin(2*PI*frequency*x + phase) + y_intercept
    """
    def sine_function(x):
        return amplitude*np.sin(2*np.pi*frequency*x + phase) + y_intercept

    return sine_function

def substract_model(data, sine):
    """
    Substract a single sine from the data.

    Parameters
    ----------
    data : ndarray
        An ndarray with (n, 3)-shape storing: time, magnitude, mag's error.
    sine : function
        A single sine function with set parameters.

    Returns
    -------
    data : ndarray
        Updated data after substracted sine function from the second column.
        The first column of the data is used as an argument for the sine.
    """
    data[:,1] -= sine(data[:,0])

    return data

def approximate_sines_parameters(lightcurve, frequencies):
    """
    For given frequency fit a sine to the data and then substract it from
    the data. Return parameters for all sines functions.

    Parameters
    ----------
    lightcurve : ndarray
        An ndarray with (n, 3)-shape storing: time, magnitude, mag's error.
    frequencies : list
        A list which stores frequencies.

    Returns
    -------
    results : ndarray
        Parameters for approximate sines functions.
    """
    n_param = 4
    results = np.empty((0, n_param))

    for frequency in frequencies:
        parameters = approximate_sine_parameters(lightcurve, frequency)
        sine_function = sine(frequency, *parameters)
        lightcurve = substract_model(lightcurve, sine_function)
        parameters = np.insert(parameters, 1, frequency)
        parameters = parameters.reshape((1, n_param))
        results = np.append(results, parameters, axis=0)

    return results

def residuals_final_fitting(parameters, x, y):
    """
    Calculate function of residuals. Function is made of a sum of sines
    subtracted from the data. Each sine is described by four values stored
    in the parameters variable.

    Parameters
    ----------
    parameters : ndarray
        An ndarray with (n,)-shape storing parameters for each sine.
        n = 4*m, where m is the number of all sines functions. For two sines:
        array([amp1, freq1, phase1, y01, amp2, freq2, phase2, y02]).

    Returns
    -------
    function
        sin1(x) + sin2(x) + ... + y0 - y. Note that y0 comes only from the
        first sine, i.e. with the highest amplitude.
    """
    n_param = 4
    sum_sines = 0

    for i in range(0, len(parameters), n_param):
        par = parameters[i:i+n_param]

        if i == 0:
            sum_sines += par[0]*np.sin(2*np.pi*par[1]*x + par[2]) + par[3]
        else:
            sum_sines += par[0]*np.sin(2*np.pi*par[1]*x + par[2])

    return sum_sines - y

def final_fitting(lightcurve, init_parameters):
    """
    Fit sines to the lightcurve.

    Parameters
    ----------
    lightcurve : ndarray
        An ndarray with (n, 3)-shape storing: time, magnitude, mag's error.

    init_parameters : ndarray
        An ndarray with (n, 4)-shape storing initial parameters for each sine.

    Returns
    -------
    ndarray
        Improved parameters of sines functions.
    """
    x0 = init_parameters.flatten()
    result = least_squares(residuals_final_fitting, x0,
                           args=(lightcurve[:,0], lightcurve[:,1]))
    fitting_parameters = _replace_negative_parameters(result.x)

    return fitting_parameters.reshape((-1,4))

def _replace_negative_parameters(parameters):
    n_param = 4

    for i in range(0, len(parameters), n_param):
        par = parameters[i:i+n_param]

        if par[0] < 0.0:
            par[0] = -par[0]
            par[2] = np.pi + par[2]

        if par[2] < 0.0:
            par[2] = 2*np.pi + par[2]

    return parameters

def save_residuals(lightcurve, parameters, filename):
    """
    For given parameters calculate a sum of sines functions. Then substract
    them from the lightcurve and save residuals to the text file.

    Parameters
    ----------
    lightcurve : ndarray
        An ndarray with (n, 3)-shape storing: time, magnitude, mag's error.

    parameters : ndarray
        An ndarray with (n, 4)-shape storing parameters for each sine.

    filename : str
        A name of the file where the data will be saved to.
    """
    residuals = residuals_final_fitting(parameters.flatten(),
                                        lightcurve[:,0], lightcurve[:,1])
    lightcurve[:,1] = residuals
    np.savetxt(filename, lightcurve, fmt="%16.6f %9.4f %7.4f")

def print_parameters(parameters):
    """
    Print parameters of sines in a nice format:

    amplitude1 frequency1 phase1 y_intercept1
    amplitude2 frequency2 phase2
    amplitude3 frequency3 phase3
    ...

    y_intercept is printed only for the first sine function.

    parameters : ndarray
        An ndarray with (n, 4)-shape storing parameters for each sine.
    """
    for i, par in enumerate(parameters):
        if i == 0:
            fmt = "{0:16.10f} {1:16.10f} {2:16.10f} {3:16.10f}"
        else:
            fmt = "{0:16.10f} {1:16.10f} {2:16.10f}"
        print(fmt.format(*par))



lightcurve = np.genfromtxt("lc")
frequencies = [30.0, 11.3]

approximate_sines_parameters(lightcurve, frequencies)
