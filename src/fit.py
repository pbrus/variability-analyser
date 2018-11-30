#!/usr/bin/env python3

import numpy as np
from scipy.optimize import least_squares


def fit_approximate_sine(frequency):

    def approximate_sine(x, amplitude, phase, y_intercept):
        return amplitude*np.sin(2*np.pi*frequency*x + phase) + y_intercept

    return approximate_sine

def sine_residuals(frequency):

    def residuals(parameters, x, y):
        approximate_sine = fit_approximate_sine(frequency)
        return approximate_sine(x, *parameters) - y

    return residuals

def approximate_sine_parameters(lightcurve, frequency):
    x0 = np.array([0., 0., 0.])
    result = least_squares(sine_residuals(frequency), x0,
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
    n_param = 4
    sum_sines = 0

    for i in range(0, len(parameters), n_param):
        par = parameters[i:i+n_param]

        if i == 0:
            sum_sines += par[0]*np.sin(2*np.pi*par[1]*x + par[2]) + par[3]
        else:
            sum_sines += par[0]*np.sin(2*np.pi*par[1]*x + par[2])

    return sum_sines - y

def final_fitting(lightcurve, sines_parameters):
    x0 = sines_parameters.flatten()

    result = least_squares(residuals_final_fitting, x0,
                           args=(lightcurve[:,0], lightcurve[:,1]))

    return result.x.reshape((-1,4))


lightcurve = np.genfromtxt("lc")
frequencies = [30.0, 11.3]

approximate_sines_parameters(lightcurve, frequencies)
