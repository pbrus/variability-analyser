#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from copy import deepcopy
from warnings import filterwarnings

filterwarnings("ignore",
               message="Covariance of the parameters could not be estimated")


def read_lightcurve(filename):
    return np.loadtxt(filename, unpack=True)

def read_model(filename):
    y_intercept = np.genfromtxt(filename, max_rows=1)
    parameters = np.genfromtxt(filename, skip_header=1)

    return y_intercept, parameters

def time_to_phase(time, period):
    time_min = time.min()
    time = time - time_min
    phase = time/period - time//period

    return phase

def multiply_phase(phase, magnitude, factor):
    single_phase = deepcopy(phase)
    single_magnitude = deepcopy(magnitude)

    for i in range(1, factor):
        phase = np.append(phase, single_phase + i)
        magnitude = np.append(magnitude, single_magnitude)

    return phase, magnitude

def prepare_data(filename, frequency, phases_number):
    time, magnitude, error = read_lightcurve(filename)
    phase = time_to_phase(time, 1/frequency)
    phase, magnitude = multiply_phase(phase, magnitude, phases_number)

    return phase, magnitude

def get_model(filename, frequency, phase, magnitude):
    y_intercept, parameters = read_model(filename)
    min_phase, max_phase = round(phase.min()), round(phase.max())
    approx_sines_sum = sines_sum(parameters, y_intercept, frequency)
    x0, _ = curve_fit(approx_sines_sum, phase, magnitude, p0=0)
    X = np.linspace(min_phase, max_phase, max_phase*100)
    model = sines_sum(parameters, y_intercept, frequency)

    return X, model(X, x0)

def sines_sum(sines_parameters, y_intercept, frequency):

    def sines(x, x0):
        y = 0

        for par in sines_parameters:
            y += par[0]*np.sin(2*np.pi*par[1]/frequency*(x - x0) + par[2])

        return y + y_intercept

    return sines

def _draw_phase(phase, magnitude, markersize=2):
    plt.xlabel("Phase")
    plt.ylabel("Brightness [mag]")
    plt.gca().invert_yaxis()
    plt.plot(phase, magnitude, '.', alpha=0.5, markersize=markersize)

def _draw_model(X, Y):
    plt.plot(X, Y, 'r-', alpha=0.7)

def display_plot(phase, magnitude, model=None):
    _draw_phase(phase, magnitude, 6)

    if model != None:
        _draw_model(*model)

    plt.show()
