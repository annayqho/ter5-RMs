""" We want to find the phase shift between bands that results in the 
smallest spread of RM results. """

import os
import glob
import globalfit as g
import numpy as np
import matplotlib.pyplot as plt
import findmin as f
import calc_params

psr = 'Ter5I'
nbin = 128

Lband = 'output/%s_Lband_summed.forPA_b%s' %(psr, nbin)
os.system('cp %s %s_r' %(Lband, Lband)) # just to make life easer later on

Sband = 'output/%s_Sband_summed.forPA_b%s' %(psr, nbin)
ext = Sband.split('.')[1]

onebin = 1.0/64.0
# Search from 2 bins left to 2 bins right, step by a tenth of a bin
shifts = np.arange(-2.0*onebin, 2.0*onebin, onebin/10.0)

RM_avg = []
RM_std = []
offset_avg = []
offset_std = []


def getRM(psr):
    pair = glob.glob("output/*%s*band*.forPA_b128_r" %psr)
    lsquareds, PAs, PAerrs = calc_params.get_data(pair)
    out = calc_params.calc_RM_indbins(lsquareds, PAs, PAerrs, psr)
    return out


for shift in shifts:
    # Command to rotate the Sband summed profile by some fraction of a bin
    command = 'pam -r %s -e %s_r %s' %(shift, ext, Sband)
    print command
    os.system(command)

    # Perform the fit and record the chi sq
    out = getRM(psr)
    bins, RM_all, RMerr_all, offset_all, offseterr_all = out
    
    bad = np.logical_or(RMerr_all<0, offseterr_all<0)
    weights = 1./RMerr_all**2
    avg = np.average(RM_all[~bad], weights=weights[~bad])
    std = np.sqrt(np.average((RM_all[~bad]-avg)**2, weights=weights[~bad]))
    RM_avg.append(avg)
    RM_std.append(std)

    weights = 1./offseterr_all**2
    avg = np.average(offset_all[~bad], weights=weights[~bad])
    std = np.sqrt(np.average((offset_all[~bad]-avg)**2, weights=weights[~bad]))
    offset_avg.append(avg)
    offset_std.append(std)


min_shift, min_chisq, x, gaussian = f.findshift(psr, shifts, chisqs)
print "Min shift: %s" %min_shift
print "Min chisq: %s" %min_chisq

shifts = nbin*shifts
fig, axarr = plt.subplots(2, sharex=True)
plt.xlabel('Phase shift (nbins out of %s total)' %nbin)
axarr[0].scatter(shifts, RMs)
axarr[0].errorbar(shifts, RMs, yerr=RMerrs)
axarr[0].set_title('RM vs. Shift')
axarr[1].scatter(shifts, chisqs)
axarr[1].set_title('X2 vs. Shift')
axarr[1].plot(x, gaussian)

plt.savefig('Ter5%s_findshift.png' %psr)
#plt.show()


















