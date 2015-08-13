import glob
import numpy as np
import subprocess
import matplotlib.pyplot as plt
import globalfit as g
import read_data


def run_with_offsets(lsquareds, PAs, PAerrs):
    """ Calculate params with separate y-intercept for each bin/band combo """
    nbin = lsquareds.shape[0]
    nband = lsquareds.shape[1]
    p0 = [1] # dRM
    temp = np.zeros((nbin,nband))
    temp.fill(0.01)
    p0.append(temp)
    out = minimize(
        errfunc_offsets, p0, args=(lsquareds, PAs, PAerrs), full_output=1)
    
    

g.globalfit(
        lsquareds, PAs, PAerrs, p0, nbin, nband, offset=1)
    chisq = g.calcchisq0(dRM, b0, lsquareds, PAs, PAerrs)
    dRMerr = err[0]
    dberr = err[1]
    b0err = err[2]
    return dRM, dRMerr, b0, b0err, db, dberr, chisq


def run_with_offset(lsquareds, PAs, PAerrs):
    """ Calculate separate y-intercept for each bin and a single offset """
    nbin = lsquareds.shape[0]
    nbands = lsquareds.shape[1]
    p0 = [1] # dRM
    for i in range(nbands-1):
        p0.append(0.01) # an offset
    for i in range(nbin):
        p0.append(0.01) # y-intercept, will vary from bin to bin
    dRM, db, b0, err = g.globalfit(
        lsquareds, PAs, PAerrs, p0, nbin, nbands, offset=1)
    chisq = g.calcchisq0(dRM, b0, lsquareds, PAs, PAerrs)
    dRMerr = err[0]
    dberr = err[1]
    b0err = err[2]
    return dRM, dRMerr, b0, b0err, db, dberr, chisq


def run_with_no_offset(lsquareds, PAs, PAerrs):
    """ Calculate separate y-intercept for each bin assuming no offset """
    nbin = lsquareds.shape[0]
    nbands = lsquareds.shape[1]
    p0 = [1] # dRM
    for i in range(nbin):
        p0.append(0.01) # y-intercept, will vary from bin to bin
    dRM, b0, err = g.globalfit(
        lsquareds, PAs, PAerrs, p0, nbin, nbands, offset=1)
    chisq = g.calcchisq0(dRM, b0, lsquareds, PAs, PAerrs)
    dRMerr = err[0]
    dberr = err[1]
    return dRM, dRMerr, b0, b0err, chisq


def calc_RM_indbins(lsquareds, PAs, PAerrs, psr):
    """ Calculate an RM for each bin individually """
    nbin = lsquareds.shape[0]
    npts = np.sum(PAerrs<1e10, axis=2)
    npts_tot = np.sum(npts,axis=1)
    nptsL = npts[:,0]
    nptsS = npts[:,1]
    bins = np.arange(nbin)[npts_tot>2]
    dRM_all = []
    RMerr_all = []
    offset_all = []
    offseterr_all = []
    for b in bins:
        print(b)
        lsquareds_choose = lsquareds[b,:,:].reshape(1,2,8)
        PAs_choose = PAs[b,:,:].reshape(1,2,8)
        PAerrs_choose = PAerrs[b,:,:].reshape(1,2,8)
        dRM, offsets, phi0s, errs, chisq = calc_RM(
            lsquareds_choose, PAs_choose, PAerrs_choose)
        dRM_all.append(dRM)
        RMerr_all.append(errs[0])
        offset_all.append(offsets[0])
        offseterr_all.append(errs[1][0])
        plt.errorbar(lsquareds_choose[0,0,:], PAs_choose[0,0,:], 
                 PAerrs_choose[0,0,:], fmt='.', c='r')
        plt.errorbar(lsquareds_choose[0,1,:], PAs_choose[0,1,:],
                 PAerrs_choose[0,1,:], fmt='.', c='b')
        x = np.linspace(0.01, 0.07)
        y = dRM*x + phi0s[0]
        plt.plot(x,y,c='k')
        plt.plot(x,y+offsets[0],c='k')
        plt.ylim(0,np.pi)
        plt.xlim(0.01, 0.07)
        plt.title("%s, Bin %s" %(psr, b))
        plt.xlabel("Wavelength Squared (m^2)")
        plt.ylabel("PA (radians)")
        plt.savefig("output/%s_bin%s_fit.png" %(psr, b))
        plt.close()
    dRM_all = np.array(dRM_all)
    RMerr_all = np.array(RMerr_all)
    offset_all = np.array(offset_all)
    offseterr_all = np.array(offseterr_all)
    return bins, dRM_all, RMerr_all, offset_all, offseterr_all
