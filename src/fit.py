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

def split_frequencies(frequencies, epsilon):
    basic_freqs = frequencies[:1]
    n_freqs = len(frequencies)

    for i in range(n_freqs - 1):
        if not np.any(linear_combination(basic_freqs, frequencies[i+1],
                                         epsilon=epsilon)):
            basic_freqs.append(frequencies[i+1])

    harmonic_freqs = [freq for freq in frequencies if freq not in basic_freqs]

    return basic_freqs, harmonic_freqs

def frequencies_combination(frequencies, epsilon):
    basic_freqs, harmonic_freqs = split_frequencies(frequencies, epsilon)
    freqs_array = np.diag(np.ones(len(basic_freqs), dtype=int))

    for harm in harmonic_freqs:
        linear_comb = linear_combination(basic_freqs, harm, epsilon=epsilon)
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

def fit_final_curve(lightcurve, frequencies, epsilon=1e-3):
    approx_param = approximate_parameters(lightcurve, frequencies)
    basic_freqs, freqs_comb = frequencies_combination(frequencies, epsilon)
    func = final_sines_sum(freqs_comb)
    time, mag, err = lightcurve[:,0], lightcurve[:,1], lightcurve[:,2]
    x0 = initial_sines_sum_parameters(approx_param, basic_freqs)
    parameters, _ = curve_fit(func, time, mag, sigma=err, p0=x0)
    parameters = final_parameters(parameters, freqs_comb)

    return parameters

def final_parameters(parameters, frequencies_combination):
    base_size = frequencies_combination.shape[1]
    param = np.array(parameters[-1])
    freqs = np.dot(parameters[:base_size], frequencies_combination.T)
    n_parameters = int((len(parameters) - base_size - 1)/2)

    for i in range(n_parameters):
        param = np.append(param, parameters[2*i + base_size])
        param = np.append(param, freqs[i])
        param = np.append(param,
                          normalize_phase(parameters[2*i + 1 + base_size]))

    return param

def normalize_phase(phase):
    return phase - 2*np.pi*(phase//(2*np.pi))

def print_parameters(parameters):
    fmt = "{0:16.10f}"
    print(fmt.format(parameters[0]))
    fmt = "{0:16.10f} {1:16.10f} {2:16.10f}"

    for i, par in enumerate(parameters[1:].reshape(-1,3)):
        print(fmt.format(*par))

def sines_sum(parameters):
    par = parameters

    def func(x):
        y = 0

        for i in range(len(parameters)//3):
            i *= 3
            y += par[i+1]*np.sin(2*np.pi*par[i+2]*x + par[i+3])

        return y + par[0]

    return func

def substract_model(data, model):
    data[:,1] -= model(data[:,0])

    return data

def save_residuals(lightcurve, parameters, filename):
    model = sines_sum(parameters)
    lightcurve = substract_model(lightcurve, model)
    np.savetxt(filename, lightcurve, fmt="%16.6f %9.4f %7.4f")


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
