"""
Fit a sum of sines to the light curve.

"""
import numpy as np
from scipy.optimize import curve_fit
from math import sqrt, pow, atan2
from warnings import filterwarnings
from varana.freq_comb import coefficients_generator, linear_combination

filterwarnings("ignore",
               message="Covariance of the parameters could not be estimated")


def approximate_sines_sum(frequencies):
    """
    For given frequencies calculate a parameterized sum of sines. Each sine
    function is linearized, i.e.: A*sin(2*pi*x + fi) + y0 is equal:
    A1*sin(2*pi*x) + A2*cos(2*pi*x) + y0,
    where A = sqrt(A1^2 + A2^2), arctg(fi)=A2/A1

    Parameters
    ----------
    frequencies : list
        A list with frequencies.

    Returns
    -------
    sines_sum : function
        Parameterized sum of sines.
    """
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
    """
    Calculate an amplitude from coefficients. See approximate_sines_sum
    function.

    Parameters
    ----------
    coefficients : ndarray
       A (2,)-shape array with two coefficients.

    Returns
    -------
    float
        A value of the amplitude.
    """

    return sqrt(sum(map(lambda x: pow(x, 2), coefficients)))


def phase(coefficients):
    """
    Calculate a phase from coefficients. See approximate_sines_sum function.

    Parameters
    ----------
    coefficients : ndarray
       A (2,)-shape array with two coefficients.

    Returns
    -------
    float
        A phase angle from (0, 2pi) interval.
    """
    ph = atan2(*coefficients[::-1])

    if ph < 0.0:
        ph += 2*np.pi

    return ph


def convert_linear_parameters(parameters):
    """
    Convert all A1, A2 parameters of sum of sines function to amplitudes and
    phases. For more info see approximate_sines_sum function.

    Parameters
    ----------
    parameters : ndarray
       An array with all parameters of sum of sines function.

    Returns
    -------
    parameters : ndarray
        An array with replaced coefficients by amplitudes and phases.
    """
    for param in parameters.reshape(-1, 3):
        amp = amplitude(param[:2])
        ph = phase(param[:2])
        param[0] = amp
        param[1] = ph

    return parameters


def add_frequencies(parameters, frequencies):
    """
    Add frequencies to the array with parameters of sum of sines function.

    Parameters
    ----------
    parameters : ndarray
       An array with all parameters of sum of sines function without
       frequencies.
    frequencies : list
        A list with all frequencies delivered by input.

    Returns
    -------
    updated_parameters : ndarray
        A new (-1,4)-shape array supplemented by the frequencies.
    """
    updated_parameters = np.empty(0).reshape(0, 4)

    for parameter, frequency in zip(parameters.reshape(-1, 3), frequencies):
        parameter = np.insert(parameter, 1, frequency)
        updated_parameters = np.append(updated_parameters, parameter)

    return updated_parameters.reshape(-1, 4)


def fit_approximate_curve(lightcurve, frequencies):
    """
    Fit an approximate curve to the light curve using a linear least squares
    method. The curve is composed of a sum of sines. Each sine has defined
    frequency.

    Parameters
    ----------
    lightcurve : ndarray
       An array composed of three columns: time, magnitude, errors.
    frequencies : list
        A list with all frequencies delivered by input.

    Returns
    -------
    parameters : ndarray
        An array with parameters which describe approximate_sines_sum function.
    """
    func = approximate_sines_sum(frequencies)
    time, mag, err = lightcurve[:, 0], lightcurve[:, 1], lightcurve[:, 2]
    x0 = np.zeros(3*len(frequencies))
    parameters, _ = curve_fit(func, time, mag, sigma=err, p0=x0)

    return parameters


def approximate_parameters(lightcurve, frequencies):
    """
    Calculate parameters of an approximate sum of sines.

    Parameters
    ----------
    lightcurve : ndarray
       An array composed of three columns: time, magnitude, errors.
    frequencies : list
        A list with all frequencies delivered by input.

    Returns
    -------
    parameters : ndarray
        An array with parameters which describe each sine, i.e.: amplitude,
        frequency, phase, y intercept.
    """
    parameters = fit_approximate_curve(lightcurve, frequencies)
    parameters = convert_linear_parameters(parameters)
    parameters = add_frequencies(parameters, frequencies)

    return parameters


def final_sines_sum(linear_combination):
    """
    For given linear combination of basic frequencies return parameterized
    sum of sines.

    Parameters
    ----------
    linear_combination : ndarray
       An (n,m)-shape array with integers. n denotes a number of all
       frequencies (base and their combinations), m indicates a number of basic
       frequencies.

    Returns
    -------
    sines_sum : function
        The parameterized sum of sines.
    """
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
    """
    Split frequencies into two lists.

    Parameters
    ----------
    frequencies : list
        A list with frequencies.
    epsilon : float
        If a single frequency is compared to the linear combination of another
        frequencies, the epsilon means tolerance in this comparison.

    Returns
    -------
    tuple
        A tuple made of two list. The first one contains basic frequencies, the
        second one their combinations.
    """
    basic_freqs = frequencies[:1]
    n_freqs = len(frequencies)

    for i in range(n_freqs - 1):
        if not np.any(linear_combination(basic_freqs, frequencies[i+1],
                                         epsilon=epsilon)):
            basic_freqs.append(frequencies[i+1])

    comb_freqs = [freq for freq in frequencies if freq not in basic_freqs]

    return basic_freqs, comb_freqs


def frequencies_combination(frequencies, epsilon):
    """
    Select from all frequencies only those which are independent and generate
    an array with coefficients of a linear combinations of basic frequencies.

    Parameters
    ----------
    frequencies : list
        A list with frequencies.
    epsilon : float
        If a single frequency is compared to the linear combination of another
        frequencies, the epsilon means tolerance in this comparison.

    Returns
    -------
    tuple
        A tuple made of a list and an ndarray. The first one contains basic
        frequencies, the second one the array with coefficients of linear
        combinations of basic frequencies.
    """
    basic_freqs, harmonic_freqs = split_frequencies(frequencies, epsilon)
    freqs_array = np.diag(np.ones(len(basic_freqs), dtype=int))

    for harm in harmonic_freqs:
        linear_comb = linear_combination(basic_freqs, harm, epsilon=epsilon)
        linear_comb = linear_comb.reshape(-1, len(basic_freqs))
        freqs_array = np.append(freqs_array, linear_comb, axis=0)

    return basic_freqs, freqs_array


def initial_sines_sum_parameters(approximate_parameters, basic_frequencies):
    """
    Prepare initial parameters for the sum of sines function.

    Parameters
    ----------
    approximate_parameters : ndarray
        A list with parameters for each sine, i.e. amplitude, frequency,
        phase, y0.
    basic_frequencies : list
        A list with basic frequencies.

    Returns
    -------
    parameters : ndarray
        Initial parameters for further fitting.
    """
    parameters = np.array(basic_frequencies)
    amplitudes_phases = np.append(approximate_parameters[:, :1],
                                  approximate_parameters[:, 2:3],
                                  axis=1).flatten()
    parameters = np.append(parameters, amplitudes_phases)
    parameters = np.append(parameters, approximate_parameters[:, -1].sum())

    return parameters


def fit_final_curve(lightcurve, frequencies, epsilon=1e-3):
    """
    Fit a final curve to the light curve using a non-linear least squares
    method. The curve is composed of a sum of sines. The frequency parameters
    are limited only to basic frequencies. Some sines can be harmonics or have
    frequencies equal to linear combinations of the basic frequencies.

    Parameters
    ----------
    lightcurve : ndarray
       An array composed of three columns: time, magnitude, errors.
    frequencies : list
        A list with all frequencies delivered by input.
    epsilon : float
        If a single frequency is compared to the linear combination of another
        frequencies, the epsilon means tolerance in this comparison.

    Returns
    -------
    parameters : ndarray
        An array with parameters which describe a fitted function.
    """
    basic_freqs, freqs_comb = frequencies_combination(frequencies, epsilon)
    approx_param = approximate_parameters(lightcurve,
                                          np.dot(basic_freqs, freqs_comb.T))
    func = final_sines_sum(freqs_comb)
    time, mag, err = lightcurve[:, 0], lightcurve[:, 1], lightcurve[:, 2]
    x0 = initial_sines_sum_parameters(approx_param, basic_freqs)
    parameters, _ = curve_fit(func, time, mag, sigma=err, p0=x0)
    parameters = final_parameters(parameters, freqs_comb)

    return parameters


def final_parameters(parameters, frequencies_combination):
    """
    Reformat parameters from a non-linear least squares fitting which describe
    a fitted curve. The curve is composed of sum of sines function.

    Parameters
    ----------
    parameters : ndarray
       An array with parameters. This array contains only basic frequencies and
       the rest of the parameters.
    frequencies_combination : ndarray
       An (n,m)-shape array with integers. n denotes a number of all
       frequencies (base and their combinations), m indicates basic
       frequencies.

    Returns
    -------
    param : ndarray
        Reformatted parameters. For each fitted sine function this array
        contains a set of parameters: amplitude, frequency, phase and one
        y0 value for the fitted curve.
    """
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
    """
    Shift a phase angle to the (0, 2*pi) interval.

    Parameters
    ----------
    phase : float
        A value of phase in radians.
    """
    return phase - 2*np.pi*(phase//(2*np.pi))


def print_parameters(parameters):
    """
    Print parameters of sines in a nice format:

    y_intercept
    amplitude1 frequency1 phase1
    amplitude2 frequency2 phase2
    amplitude3 frequency3 phase3
    ...

    Parameters
    ----------
    parameters : ndarray
        y0, amplitude1, frequency1, phase1, amplitude2, frequency2, phase2, ...
    """
    fmt = "{0:16.10f}"
    print(fmt.format(parameters[0]))
    fmt += " {1:16.10f} {2:16.10f}"

    for i, par in enumerate(parameters[1:].reshape(-1, 3)):
        print(fmt.format(*par))


def sines_sum(parameters):
    """
    Construct sum of sines for given parameters.

    Parameters
    ----------
    parameters : ndarray
        y0, amplitude1, frequency1, phase1, amplitude2, frequency2, phase2, ...

    Returns
    -------
    function
        f(x) = amplitude1*sin(2*pi*frequency1*x + phase1) +
               amplitude2*sin(2*pi*frequency2*x + phase2) + ... + y0
    """
    par = parameters

    def func(x):
        y = 0

        for i in range(len(parameters)//3):
            i *= 3
            y += par[i+1]*np.sin(2*np.pi*par[i+2]*x + par[i+3])

        return y + par[0]

    return func


def substract_model(data, model):
    """
    Substract a model from the second column of the data.

    Parameters
    ----------
    data : ndarray
        The data composed of two columns at least.
    model : function
        A function which describes the model.

    Returns
    -------
    data : ndarray
        Updated data: column2 = column2 - model(column1)
    """
    data[:, 1] -= model(data[:, 0])

    return data


def save_residuals(lightcurve, parameters, filename):
    """
    Save residuals of a light curve to the file.

    Parameters
    ----------
    lightcurve : ndarray
        An ndarray with (n, 3)-shape storing: time, magnitude, mag's error.

    parameters : ndarray
        An ndarray which stores parameters for each sine.

    filename : str
        A name of the file where the data will be saved to.
    """
    model = sines_sum(parameters)
    lightcurve = substract_model(lightcurve, model)
    np.savetxt(filename, lightcurve, fmt="%16.6f %9.4f %7.4f")
