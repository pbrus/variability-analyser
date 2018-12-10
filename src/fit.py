#!/usr/bin/env python3

import numpy as np
from scipy.optimize import curve_fit
from math import sqrt, pow, atan2
from copy import deepcopy
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from textwrap import dedent
from freq_comb import coefficients_generator, linear_combination


def approximate_sines_sum(frequencies):

    def sines_sum(x, *sines_parameters):
        param = sines_parameters
        func = 0

        for i, frequency in enumerate(frequencies):
            i *= 3
            func += (param[i]*np.sin(2*np.pi*frequency*x)
                     + param[i+1]*np.cos(2*np.pi*frequency*x)
                     + param[i+2])

        return func

    return sines_sum

def amplitude(coefficients):
    pow2 = lambda x: pow(x, 2)

    return sqrt(sum(map(pow2, coefficients)))

def phase(coefficients):
    ph = atan2(*coefficients[::-1])

    if ph < 0.0:
       ph += 2*np.pi

    return ph

def convert_linear_parameters(parameters):

    for param in parameters.reshape(3,-1):
        amp = amplitude(param[:2])
        ph = phase(param[:2])
        param[0] = amp
        param[1] = ph

    return parameters

def add_frequencies(parameters, frequencies):
    updated_parameters = np.empty(0).reshape(0,4)

    for parameter, frequency in zip(parameters.reshape(-1,3), frequencies):
        parameter = np.insert(parameter, 1, frequency)
        updated_parameters = np.append(updated_parameters, parameter)

    return updated_parameters.reshape(-1,4)

def fit_approximate_curve(lightcurve, frequencies):
    func = approximate_sines_sum(frequencies)
    time, mag, err = lightcurve[:,0], lightcurve[:,1], lightcurve[:,2]
    x0 = np.zeros(3*len(frequencies))
    parameters, _ = curve_fit(func, time, mag, sigma=err, p0=x0)

    return parameters

def approximate_parameters(lightcurve, frequencies):
    parameters = fit_approximate_curve(lightcurve, frequencies)
    parameters = convert_linear_parameters(parameters)
    parameters = add_frequencies(parameters, frequencies)

    return parameters

def final_sines_sum(linear_combination):

    def sines_sum(x, *param):
        m, n = linear_combination.shape
        func = 0

        for i in range(m):
            frequency = np.dot(param[:n], linear_combination[i])
            i *= 2
            func += (param[n+i]*np.sin(2*np.pi*frequency*x + param[n+i+1]))

        return func + param[-1]

    return sines_sum

def split_frequencies(frequencies):
    basic_freqs = frequencies[:1]
    n_freqs = len(frequencies)

    for i in range(n_freqs - 1):
        if not np.any(linear_combination(basic_freqs, frequencies[i+1])):
            basic_freqs.append(frequencies[i+1])

    harmonic_freqs = [freq for freq in frequencies if freq not in basic_freqs]

    return basic_freqs, harmonic_freqs

def frequencies_combination(frequencies):
    basic_freqs, harmonic_freqs = split_frequencies(frequencies)
    freqs_array = np.diag(np.ones(len(basic_freqs), dtype=int))

    for harm in harmonic_freqs:
        linear_comb = linear_combination(basic_freqs, harm)
        linear_comb = linear_comb.reshape(-1, len(basic_freqs))
        freqs_array = np.append(freqs_array, linear_comb, axis=0)

    return basic_freqs, freqs_array

def initial_sines_sum_parameters(approximate_parameters, basic_frequencies):
    parameters = np.array(basic_frequencies)
    amplitudes_phases = np.append(approximate_parameters[:,:1],
                                  approximate_parameters[:,2:3],
                                  axis=1).flatten()
    parameters = np.append(parameters, amplitudes_phases)
    parameters = np.append(parameters, approximate_parameters[:,-1].sum())

    return parameters

def fit_final_curve(lightcurve, frequencies):
    approx_param = approximate_parameters(lightcurve, frequencies)
    basic_freqs, freqs_comb = frequencies_combination(frequencies)
    func = final_sines_sum(freqs_comb)
    time, mag, err = lightcurve[:,0], lightcurve[:,1], lightcurve[:,2]
    x0 = initial_sines_sum_parameters(approx_param, basic_freqs)
    parameters, _ = curve_fit(func, time, mag, sigma=err, p0=x0)

    return parameters

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


if __name__ == "__main__":
    argparser = ArgumentParser(
        prog='fit.py',
        description='>> Fit a sum of sines to the lightcurve <<',
        epilog='Copyright (c) 2018 Przemysław Bruś',
        formatter_class=RawTextHelpFormatter
    )

    argparser.add_argument(
        'lightcurve',
        help=dedent('''\
        The name of a file which stores lightcurve data.
        ------------------------------------
        The file must contain three columns:
        time magnitude magnitude_error

        ''')
    )

    argparser.add_argument(
        '--freq',
        help=dedent('''\
        A list of frequencies for each sine.

        '''),
        nargs='+',
        metavar='f1',
        type=float,
        required=True
    )

    argparser.add_argument(
        '--resid',
        help=dedent('''\
        A name of the file storing residuals.

        '''),
        metavar='filename',
        type=str
    )

    args = argparser.parse_args()
    try:
        lightcurve = np.genfromtxt(args.lightcurve)
    except OSError as error:
        print(error)
        exit()

    lightcurve_org = deepcopy(lightcurve)
    frequencies = args.freq
    sines_parameters = approximate_sines_parameters(lightcurve, frequencies)
    final_parameters = final_fitting(lightcurve_org, sines_parameters)
    print_parameters(final_parameters)

    if args.resid != None:
        save_residuals(lightcurve_org, final_parameters, args.resid)
