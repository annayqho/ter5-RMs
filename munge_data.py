import os
import subprocess
import glob
import globalfit as g
import itertools
import numpy as np
import math as m
import matplotlib.pyplot as plt

def preparefiles(psr, RM0):
    # Correct for preliminary rotation measure
    call = 'pam -R %s -e rm_tscr Ter5%s*.tscr' %(RM0, psr)
    print call
    os.system(call)

    # Line up between bands
    for file in glob.glob('Ter5%s*.rm_tscr' %psr): # for each band,
        out = subprocess.check_output(['psrstat', '-c', 'nbin', file])
        out2 = out.split('=')[1]
        nbins = out2.split('\n')[0]
        template = 'Ter5%s_%s_gaussians.template' %(psr, nbins)
        out = subprocess.check_output(['pat', '-R', '-TF', '-s', template, file])
        rotateby = out.split(' ')[3]
        os.system("pam -r %s -e autorot %s" %(rotateby, file))

    # Now bin the data to prepare it for fitting
    # - The bin scrunching amount should depend on how broad the profile is...may have to come back and check on this part

    call = "pam --setnbin 64 --setnchn 8 -e forPA_b64 Ter5%s*.autorot" %psr
    print call
    os.system(call)

    call = "pam --setnbin 128 --setnchn 8 -e forPA_b128 Ter5%s*.autorot" %psr
    print call
    os.system(call)

    call = "pam --setnbin 256 --setnchn 8 -e forPA_b256 Ter5%s*.autorot" %psr
    print call
    os.system(call)

    ##### FITTING
    #/nimrod1/aho/RMCalculations/full_process.py
    #/nimrod1/aho/RMCalculations/globalfit.py
    files = glob.glob('Ter5%s*_b64' %(psr))
    nbin = int(files[0].split('_')[3][1:]) # read it from the filename
    bins = np.arange(nbin)
    bins = [2]
    nbands = len(files)
    lsquareds, PAs, PAerrs = g.getPAs_allbins(files, bins)
    # Plot the bin fits
    
    x = lsquareds[0].flatten()
    y = PAs[0].flatten()
    yerr = PAerrs[0].flatten()
    # print x
    # print y
    # print yerr
    #, 0.07)
    #plt.ylim(2.15, 3.15)
    plt.scatter(x, y, marker='o')
    plt.errorbar(x, y, yerr=yerr,fmt=None)
    plt.savefig('Ter5%s_bin%s_fit' %(psr, binplot))

    # Perform the fit
    p0 = [1] # dRM
    numbins = len(lsquareds)
    for i in range(0, numbins):
        p0.append(0.01) # the y-intercepts will vary from bin to bin
    lsquareds = np.array(lsquareds)
    PAs = np.array(PAs)
    PAerrs = np.array(PAerrs)
    dRM, offsets, phi0s, errs = g.globalfit(lsquareds, PAs, PAerrs, p0, numbins, nbands, offset=0)
    print "done!"
    RMerr, phi0errs = errs[0], errs[1]
    chisq = g.calcchisq0(dRM, phi0s, lsquareds, PAs, PAerrs)

    RM = float(RM0) + float(dRM)

    return RM, RMerr, chisq













 
