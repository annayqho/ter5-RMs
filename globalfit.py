import os
import math as m
import sys
import pylab as py
from scipy.optimize import *
import numpy as np
import matplotlib.pyplot as plt
import subprocess


def fitfunc(m, b0, db, x):
    """ Linear function in terms of an offset 

    Parameters
    ----------
    m: slope
    b0: y-intercept of the first band
    db: offset between the bands
    """
    return (m * x + (b0 + db))


def errfunc_offsets(p, x, y, yerr):
    """ Error function for fitting nbin x nband y-intercepts 
    
    Parameters
    ----------
    p: np array, starting values, shape (1, (nbin, nband))
    x: np array, lsquareds, shape (nbin, nband, nchan)
    y: np array, PAs, parallel to x
    yerr: np array, PAerrs, parallel to x
    """
    m = p[0]
    b0 = p[1]
    nbin = x.shape[0]
    nband = x.shape[1]
    res = np.array([(y[i,j,:]-fitfunc(m, b0[i,j], 0, x[i,j,:]))/yerr[i,j,:]
                     for ii in nbin for jj in nband])
    return np.sqrt(sum(res**2)) # add res in quadrature 


def errfunc_offset(p, x, y, yerr):
    """ Error function for fitting nbin y-intercepts and (nband-1) offsets
    
    Parameters
    ----------
    p: np array, starting values, shape (1, (nbin), (nband-1)) 
    x: np array, lsquareds, shape (nbin, nband, nchan)
    y: np array, PAs, parallel to x
    yerr: np array, PAerrs, parallel to x
    """
    m = p[0]
    b0 = p[1]
    db = p[2]
    nbin = x.shape[0]
    res0 = np.array([(y[i,0,:]-fitfunc(m, b0[i], 0, x[i,0,:]))/yerr[i,0,:]
                      for i in nbin])
    res1 = np.array([(y[i,1,:]-fitfunc(m, b0[i], db[0], x[i,1,:]))/yerr[i,1,:]
                      for i in nbin])
    return np.sqrt(sum(res0**2) + sum(res1**2))


def errfunc_no_offset(p, x, y, yerr):
    """ Error function for fitting nbin y-intercepts and 0 offset
    
    Parameters
    ----------
    p: np array, starting values, shape (1, (nbin)) 
    x: np array, lsquareds, shape (nbin, nband, nchan)
    y: np array, PAs, parallel to x
    yerr: np array, PAerrs, parallel to x
    """ 
    m = p[0]
    b0 = p[1]
    nbin = x.shape[0]
    res = np.array([(y[i,:,:].flatten()-fitfunc(m,b0[i],0,x[i,:,:].flatten()))/
                     yerr[i,:,:].flatten() for i in nbin])
    return np.sqrt(sum(res**2)) # add res in quadrature 


def globalfit(x, y, yerr, p0, numbins, numbands, offset=1):
    print "Running global fit"
    # 'offset' determines whether you want to fit for an offset between bands
    out = leastsq(gerrfunc0, p0, args=(x, y, yerr), full_output=1)
    #In this case, values 1 through END are y-intercepts
    offsets = []
    coefficients = out[0]
    RM = coefficients[0]
    phi0s = coefficients[1:]
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
