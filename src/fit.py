#!/usr/bin/env python3

import numpy as np
from scipy.optimize import least_squares


def fit_approximate_sine(frequency):

    def approximate_sine(x, amplitude, phase, y_intercept):
        return amplitude*np.sin(2*np.pi*frequency*x + phase) + y_intercept

    return approximate_sine

def compute_residuals(frequency):

    def residuals(parameters, x, y):
        approximate_sine = fit_approximate_sine(frequency)
        return approximate_sine(x, *parameters) - y

    return residuals

def approximate_sine_parameters(lightcurve, frequency):
    x0 = np.array([0., 0., 0.])
    result = least_squares(compute_residuals(frequency), x0,
                           args=(lightcurve[:,0], lightcurve[:,1]))

    return result.x

def sine(frequency, amplitude, phase, y_intercept):

    def sine_function(x):
        return amplitude*np.sin(2*np.pi*frequency*x + phase) + y_intercept

    return sine_function

def substract_model(data, sine):
    data[:,1] -= sine(data[:,0])

    return data

def approximate_sines_parameters(lightcurve, frequencies):
    results = np.empty((0,3))

    for frequency in frequencies:
        parameters = approximate_sine_parameters(lightcurve, frequency)
        sine_function = sine(frequency, *parameters)
        lightcurve = substract_model(lightcurve, sine_function)
        parameters = np.insert(parameters, -1, frequency)
        results = np.append(results, parameters.reshape((1,4)))

    return results


lightcurve = np.genfromtxt("lc")
frequencies = [30.0, 11.3]

approximate_sines_parameters(lightcurve, frequencies)
