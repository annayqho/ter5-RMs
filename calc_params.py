import glob
import numpy as np
import subprocess
import matplotlib.pyplot as plt
import globalfit as g

def diagnostic_npts(lsquareds, PAs, PAerrs, psr):
    """ Plot the distribution of the number of points across the profile """
    npts = np.sum(np.sum(PAerrs<1e10, axis=2), axis=1)
    nptsL = np.sum(PAerrs[:,0,:]<1e10, axis=1)
    nptsS = np.sum(PAerrs[:,1,:]<1e10, axis=1)
    nbins = len(npts)
    x = np.arange(nbins)
    plt.bar(x, nptsL, color='r', alpha=0.5, label="L band")
    plt.bar(x, nptsS, color='b', alpha=0.5, bottom=nptsL, label="S band")
    plt.legend()
    plt.xlabel("Bin")
    plt.ylabel("Number of Points")
    plt.title("%s: Distribution of Number of Points Across Pulse Profile" %psr)
    plt.savefig("output/dist_npts_%s.png" %psr)
    plt.close()


def diagnostic_raw_data(lsquareds, PAs, PAerrs, psr):
    """ Plot the raw data in the best bin for one pulsar """
    npts = np.sum(np.sum(PAerrs<1e10, axis=2), axis=1)
    b = np.argmax(npts)
    plotx = lsquareds[b,0,:]
    ploty = PAs[b,0,:]
    plotyerr = PAerrs[b,0,:]
    plt.errorbar(plotx, ploty, yerr=plotyerr, c='r', fmt='.', label="L band")
    plotx = lsquareds[b,1,:]
    ploty = PAs[b,1,:]
    plotyerr = PAerrs[b,1,:]
    plt.errorbar(plotx, ploty, yerr=plotyerr, c='b', fmt='.', label="S band")
    plt.ylim(0, np.pi)
    plt.xlabel("Wavelength Squared")
    plt.ylabel("PA, Radians")
    plt.title("%s: Sample Pts, Bin %s" %(psr, b))
    plt.savefig("output/sample_pts_%s.png" %psr)
    plt.close()


def get_data(pair):
    nbands = len(pair)
    psr = pair[0].split('/')[1]
    psr = psr.split('_')[0]
    nbin = int(pair[0].split('_')[3][1:])
    print("getting data points")
    lsquareds, PAs, PAerrs = g.getPAs_allbins(pair, nbin)
    # diagnostic_npts(lsquareds, PAs, PAerrs, psr)
    # diagnostic_raw_data(lsquareds, PAs, PAerrs, psr)
    return lsquareds, PAs, PAerrs


def get_fileRM(filename):
    """ Read the RM from a file """
    out = subprocess.check_output(
        ['psrstat', '-c', 'rm', 'output/Ter5C_Lband_summed.forPA_b128'])    
    return (out.split()[1]).split('=')[1]


def calc_RM(lsquareds, PAs, PAerrs):
    nbin = lsquareds.shape[0]
    nbands = lsquareds.shape[1]
    p0 = [1] # dRM
    # this is JUST when fitting for an offset
    for i in range(nbands-1):
        p0.append(0.01) # an offset
    for i in range(nbin):
        p0.append(0.01) # y-intercept, will vary from bin to bin
    dRM, offsets, phi0s, errs = g.globalfit(
        lsquareds, PAs, PAerrs, p0, nbin, nbands, offset=1)
    chisq = g.calcchisq0(dRM, phi0s, lsquareds, PAs, PAerrs)
    return dRM, offsets, phi0s, errs, chisq 


def bin_consistency_test(lsquareds, PAs, PAerrs, psr):
    nbin = lsquareds.shape[0]
    npts = np.sum(np.sum(PAerrs<1e10, axis=2), axis=1)
    bins = np.arange(nbin)[npts>2]
    RM_all = []
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
        RM = float(RM0) + float(dRM)
        RM_all.append(RM)
        RMerr_all.append(errs[0])
        offset_all.append(offsets[0])
        offseterr_all.append(errs[1][0])
        errorbar(lsquareds_choose[0,0,:], PAs_choose[0,0,:], 
                 PAerrs_choose[0,0,:], fmt='.', c='r')
        errorbar(lsquareds_choose[0,1,:], PAs_choose[0,1,:],
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
    RM_all = np.array(RM_all)
    RMerr_all = np.array(RMerr_all)
    offset_all = np.array(offset_all)
    offseterr_all = np.array(offseterr_all)
    errorbar(bins, RM_all-np.average(RM_all, weights=1./RMerr_all**2), 
             yerr=RMerr_all, fmt='.', c='k')
    axhline(y=0, c='r')
    xlim(min(bins)-1, max(bins)+1)
    xlabel("Bin")
    ylabel("RM - avg(RM)")
    title("Best-Fit RM For Individual Bins with >2 points")
    savefig("output/%s_RMfits_acrossbins.png" %psr)
    errorbar(bins, 
             offset_all-np.average(offset_all, weights=1./offseterr_all**2),
             yerr=offseterr_all, fmt='.', c='k')
    axhline(y=0, c='r')
    xlim(min(bins)-1, max(bins)+1)
    xlabel("Bin")
    ylabel("Offset - avg(Offset)")
    title("Best-Fit Offset For Individual Bins with >2 points")
    savefig("output/%s_offsetfits_acrossbins.png" %psr)
    

def run_singlepsr(psr):
    fileL = glob.glob("output/%s*Lband*.forPA_b128" %psr)[0]
    fileS = glob.glob("output/%s*Sband*.forPA_b128" %psr)[0]
    pair = [fileL, fileS]
    print(pair)
    RM0 = get_fileRM(pair[0])
    lsquareds, PAs, PAerrs = get_data(pair) # (nbin, nband, nchan)
    dRM, offsets, phi0s, errs, chisq = calc_RM(lsquareds, PAs, PAerrs)
    RM = float(RM0) + float(dRM)        
    return RM, errs[0], offsets, errs[1]
 

def run():
    filesL = np.sort(glob.glob("output/*Lband*.forPA_b128"))
    filesS = np.sort(glob.glob("output/*Sband*.forPA_b128"))
    npsr = len(filesL)
    for i in range(npsr):
        pair = [filesL[i], filesS[i]]
        print(pair)
        RM0 = get_fileRM(pair[0])
        lsquareds, PAs, PAerrs = get_data(pair) # (nbin, nband, nchan)
        dRM, offsets, phi0s, errs, chisq = calc_RM(lsquareds, PAs, PAerrs)
        RM = float(RM0) + float(dRM)        
        print(RM, RMerr, chisq)
