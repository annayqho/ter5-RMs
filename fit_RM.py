import glob
import numpy as np
import globalfit as g

def fit_RM(filenames):
    nbin = int(filenames[0].split('_')[3][1:])
    print("getting data points")
    lsquareds, PAs, PAerrs = g.getPAs_allbins(filenames, nbin)
    p0 = [1] # dRM
    for i in range(len(lsquareds)):
        p0.append(0.01) # will vary from bin to bin
    #dRM, offsets, phi0s, errs = g.globalfit(
    #    lsquareds, PAs, PAerrs, p0, numbins, nbands, offset=0)
    #RMerr, phi0errs = errs[0], errs[1]
    #chisq = g.calcchisq0(dRM, phi0s, lsquareds, PAs, PAerrs)
    #RM = float(RM0) + float(dRM)
    #return RM, RMerr, chisq
    return lsquareds, PAs, PAerrs    


def run():
    filesL = np.sort(glob.glob("output/*Lband*.forPA_b128*"))
    filesS = np.sort(glob.glob("output/*Sband*.forPA_b128*"))
    npsr = len(filesL)
    #for i in range(npsr):
    for i in range(npsr):
        pair = [filesL[i], filesS[i]]
        print(pair)
        fit_RM(pair)
