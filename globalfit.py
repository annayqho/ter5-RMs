# This uses the scripts globalfit_2_linear_multibin, globalfit_linear_singlebin, and read_forPA_2 
# and merges them into one.

import os
import math as m
import sys
import pylab as py
from scipy.optimize import *
import numpy as np
import matplotlib.pyplot as plt
import subprocess


def fitfunc(m, b, x):
    """ Simple linear function """
	return (m*x+b)


def errfunc(p, x, y, yerr):
    """ Residual for a simple line """
    m = p[0]
    b = p[1]
    return (fitfunc1(m, b, x)-y)/yerr


def gfitfunc(m, b0, db, x):
    """ Linear function in terms of an offset 

    Parameters
    ----------
    m: slope
    b0: y-intercept of the first band
    db: offset between the bands
    """
	return (m * x + (b0 + db))


def gerrfunc(p, x, y, yerr):
    """ Error function for the global fit

    Parameters
    ----------
    p: np array, starting values
    x: np array, l squareds, shape nbin x nbands x nchan
    y: np array, PAs, parallel to x
    yerr: np array, PAerrs, parallel to x
    """
    numbins = x.shape[0]
    numbands = x.shape[1]
    returns = []
    m = p[0]
    offsets = []
    for i in range(1, numbands):
        offsets.append(p[i])
    b0s = []
    for i in range(numbands, len(p)):
        b0s.append(p[i])
    for b in range(0, numbins):
        for band in range(0, numbands):
            xdata = np.array(x[b][band])
            ydata = np.array(y[b][band])
            yerrdata = np.array(yerr[b][band])
            if band == 0: offset = 0
            else: offset = offsets[band-1]
            err = (gfitfunc(m, b0s[b], offset, xdata)-ydata)/yerrdata
            for element in err:
                returns.append(element)
    return returns


def gerrfunc0(p, x, y, yerr):
    """ For the global fit, assuming zero offset between bands """
    numbins = len(x)
    returns = []
    m = p[0] # one
    b0s = [] # one per bin
    for i in range(1, len(p)):
        b0s.append(p[i])
    for b in range(0, numbins):
        xdata = np.array(x[b][0])
        ydata = np.array(y[b][0])
        yerrdata = np.array(yerr[b][0])
        err = (fitfunc1(m, b0s[b], xdata)-ydata)/yerrdata
        for element in err:
            returns.append(element)
    return returns


def linearfit1(x, y, yerr, initialvals):
	p0 = initialvals
	out = leastsq(errfunc1, p0, args=(x, y, yerr), full_output=1)
	coefficients = out[0]
	covar = out[1]
	errs = [covar[0][0], covar[1][1]]
	return coefficients, errs


def globalfit(x, y, yerr, p0, numbins, numbands, offset=1):
    print "Running global fit"
    # 'offset' determines whether you want to fit for an offset between bands
    if offset == 0:
        print "Not fitting for an offset..."
        out = leastsq(gerrfunc0, p0, args=(x, y, yerr), full_output=1)
        #In this case, values 1 through END are y-intercepts
        offsets = []
        coefficients = out[0]
        RM = coefficients[0]
        phi0s = coefficients[1:]
    else:
        print "Fitting for an offset..."
        out = leastsq(gerrfunc, p0, args=(x, y, yerr), full_output=1)
        # In this case, values 1 through numbands are offsets
        coefficients = out[0]
        RM = coefficients[0]
        offsets = coefficients[1:numbands]
        phi0s = coefficients[numbands:]
    covar = out[1]
    if offset == 0:
        errs = uncertainty0(covar, numbins, numbands)
    if offset == 1:
        errs = uncertainty(covar, numbins, numbands)
    return RM, offsets, phi0s, errs

	
def calcchisq1(rm, phi0, x, y, yerr, dof):
    totchisq = 0
    numdata = len(x)
    for i in range(0, numdata):
        xval, yval, yerrval = x[i], y[i], yerr[i]
        err = (fitfunc1(rm, phi0, xval)-yval)/yerrval
        totchisq += err**2
    normchisq = totchisq / (numdata - dof)
    return normchisq


def calcchisq0(rm, phi0s, x, y, yerr):
    """ This version is for no offset """
    totchisq, numdata = 0, 0
    numbins = len(phi0s)
    numbands = len(x[0])
    dof = numbins
    print "numbins: %s" %numbins
    print "numbands: %s" %numbands
    for i in range(0, numbins):
        for j in range(0, numbands):
            err = (gfitfunc(rm, phi0s[i], 0, x[i][j])-y[i][j])/yerr[i][j]
            chisq = sum(err**2)
            #print len(x[i][j])
            numdata += len(x[i][j])
            totchisq += chisq
   
    #print numdata
    #print dof 
    normchisq = totchisq / (numdata - dof)
    return normchisq


def calcchisq(rm, offsets, phi0s, x, y, yerr):
    """ For fitting for an offset """
    totchisq, numdata = 0, 0
    numbins = len(phi0s)
    numbands = len(offsets)+1
    dof = numbins + numbands
	
    print "For %s bins..." %numbins
	
    for i in range(0, numbins):
		for j in range(0, numbands):
			if j == 0:
				offset = 0
			else:
				offset = offsets[j-1]
			#scatterwithline(x[i][j], y[i][j], yerr[i][j], rm, phi0s[i])
			err = (gfitfunc(rm, phi0s[i], offset, x[i][j])-y[i][j])/yerr[i][j]
			#print "Bin: %s" %i
			#print err
			chisq = sum(err**2)
			numdata += len(x[i][j])
			totchisq += chisq
	
    normchisq = totchisq / (numdata - dof)
    return normchisq


def uncertainty0(covar, numbins, numbands):
    """ This version is for no offset """
    errs = []
    # The covariance matrix has N diagonals, where N = numbins + numbands
    sloperr = m.sqrt(covar[0][0])
    errs.append(sloperr)
    # The number of phiAs being fitted for: numbins
    phiAerrs = []
    print numbins
    for i in range(1, numbins+1):
        phiAerrs.append(m.sqrt(covar[i][i]))
    errs.append(phiAerrs)
    return errs


def uncertainty(covar, numbins, numbands):
    """ This version is for an offset """
    errs = []
    # The covariance matrix has N diagonals, where N = numbins + numbands
    if covar[0][0] > 0: 
        sloperr = m.sqrt(covar[0][0])
    else:
        sloperr = -1 # means the fitting hasn't converged properly
    errs.append(sloperr)
    # The number of offsets being fitted for: numbands - 1
    offseterrs = []
    for i in range(1, numbands):
        if covar[i][i] > 0:
            offseterrs.append(m.sqrt(covar[i][i]))
        else:
            offseterrs.append(-1)
    errs.append(offseterrs)
    # The number of phiAs being fitted for: numbins
    phiAerrs = []
    for i in range(numbands, numbins+numbands):
        if covar[i][i] > 0:
            phiAerrs.append(m.sqrt(covar[i][i]))
        else:
            phiAerrs.append(-1)
    errs.append(phiAerrs)
    return errs
