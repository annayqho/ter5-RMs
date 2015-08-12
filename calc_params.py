import glob
import numpy as np
import globalfit as g
import matplotlib.pyplot as plt

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


def calc_RM(lsquareds, PAs, PAerrs):
    nbin = lsquareds.shape[0]
    nbands = lsquareds.shape[1]
    p0 = [1] # dRM
    for i in range(nbin):
        p0.append(0.01) # will vary from bin to bin
    dRM, offsets, phi0s, errs = g.globalfit(
        lsquareds, PAs, PAerrs, p0, nbin, nbands, offset=1)
    RMerr, phi0errs = errs[0], errs[1]
    chisq = g.calcchisq0(dRM, phi0s, lsquareds, PAs, PAerrs)
    RM = float(RM0) + float(dRM)
    return RM, RMerr, chisq


def run():
    filesL = np.sort(glob.glob("output/*Lband*.forPA_b128*"))
    filesS = np.sort(glob.glob("output/*Sband*.forPA_b128*"))
    npsr = len(filesL)
    for i in range(npsr):
        pair = [filesL[i], filesS[i]]
        print(pair)
        lsquareds, PAs, PAerrs = get_data(pair) # (nbin, nband, nchan)
        calc_RM(lsquareds, PAs, PAerrs)
