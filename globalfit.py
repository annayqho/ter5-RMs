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


def getPAs_singlebin(filename, b):
    """ Run the pdv command to extract PAs and PAerrors from a single bin """
    output = subprocess.check_output(
        ['pdv', '-j', 'R 0', '-b %s' %b, '-Z', '-A', '-L 3', filename])
    output_split = np.array(output.split())[14:]
    nrows = 8
    ncols = len(output_split)/nrows
    rows = output_split.reshape((nrows,ncols))
    freqs = rows[:,5].astype(float)
    lsquareds = np.array([ftolsquared(f) for f in freqs])
    PAerrs = rows[:,ncols-1].astype(float) * m.pi/180.
    PAerrs[PAerrs == 0] = 1e10 # ignore these data points in the fit
    # it's easier to handle the data when it's between 0 and pi rather than 
    # -pi/2 and pi/2
    PAs = rows[:,ncols-2].astype(float) * m.pi/180. + m.pi/2
    return lsquareds, PAs, PAerrs

	
def getPAs_allbins(filenames, nbin):
    """ Extract PAs and PAerrs from all input files """
    nchan = 8
    nband = 2
    lsquareds = np.zeros((nbin, nband, nchan)) 
    PAs = np.zeros(lsquareds.shape)
    PAerrs = np.zeros(lsquareds.shape)
    for b in range(nbin):
        data = np.array(
            [getPAs_singlebin(f, b) for f in filenames]) #nband,3,nchan
        ltemp = data[:,0,:]
        PAtemp = data[:,1,:]
        PAerrtemp = data[:,2,:] 
        # Test for wrapping cases
        flatl = ltemp.flatten()
        flatPA = PAtemp.flatten()
        flatPAerr = PAerrtemp.flatten()
        testPA = (flatPA + np.pi/2)%np.pi
        if np.round(std_w(testPA, 1./flatPAerr),5) < \
            np.round(std_w(flatPA, 1./flatPAerr),5):
            print "wrapping in bin %s" %str(b)
            PAs[b,:,:] = (PAtemp + np.pi/2)%np.pi
        else:
            PAs[b,:,:] = PAtemp
        lsquareds[b,:,:] = ltemp
        PAerrs[b,:,:] = PAerrtemp     
    return np.array(lsquareds), np.array(PAs), np.array(PAerrs)


def fitfunc1(m, b, x):
	return (m*x+b)


def sawfitfunc1(m, b, K, x):
	return (m*x+b)%K


def gfitfunc(m, b0, db, x):
	# db is the offset
	# b0 is the y-intercept of the bins in the first band
	return (m * np.array(x) + (b0 + db))


def errfunc1(p, x, y, yerr):
    """ For a basic line """
	returns = []
	m = p[0]
	b = p[1]
	return (fitfunc1(m, b, x)-y)/yerr


def gerrfunc(p, x, y, yerr, numbands):
    """ For the global fit, assuming a constant offset between bands. """
	numbins = len(x)
	returns = []
	m = p[0]
	offsets = []
	for i in range(1, numbands):
		offsets.append(p[i])
	b0s = []
	for i in range(numbands, len(p)):
		b0s.append(p[i])
	for bin in range(0, numbins):
		for band in range(0, numbands):
			xdata = np.array(x[bin][band])
			ydata = np.array(y[bin][band])
			yerrdata = np.array(yerr[bin][band])
			if band == 0: offset = 0
			else: offset = offsets[band-1]
			err = (gfitfunc(m, b0s[bin], offset, xdata)-ydata)/yerrdata
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
    for bin in range(0, numbins):
        xdata = np.array(x[bin][0])
        ydata = np.array(y[bin][0])
        yerrdata = np.array(yerr[bin][0])
        err = (fitfunc1(m, b0s[bin], xdata)-ydata)/yerrdata
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


def globalfit(x, y, yerr, initialvals, numbins, numbands, offset=1):
    print "Running global fit"
    p0 = initialvals
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
        out = leastsq(gerrfunc, p0, args=(x, y, yerr, numbands), full_output=1)
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
    sloperr = m.sqrt(covar[0][0])
    errs.append(sloperr)
    # The number of offsets being fitted for: numbands - 1
    offseterrs = []
    for i in range(1, numbands):
            offseterrs.append(m.sqrt(covar[i][i]))
    errs.append(offseterrs)
    # The number of phiAs being fitted for: numbins
    phiAerrs = []
    for i in range(numbands, numbins+numbands):
            phiAerrs.append(m.sqrt(covar[i][i]))
    errs.append(phiAerrs)
    return errs
