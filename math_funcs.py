""" A few useful functions """
import math as m
import numpy as np


def ftolsquared(frequency):
    """ Convert from frequency in MHz to wavelength squared in m^2 """
    c = 3.0*pow(10, 8)
    freq = frequency * pow(10, 6)
    wavelength = c / freq
    wavelength_squared = pow(wavelength, 2)
    return wavelength_squared


def std_w(values, weights):
    """ Returns the weighted standard deviation of a set of values """
    average = np.average(values, weights=weights)
    variance = np.average((values-average)**2, weights=weights)
    return m.sqrt(variance)
