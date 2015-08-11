import glob
import numpy as np
import globalfit as g

def fit_RM(filenames):
    nbin = int(filenames[0].split('_')[3][1:])
    lsquareds, PAs, PAerrs = g.getPAs_allbins(filenames, nbin)


def run():
    filesL = np.sort(glob.glob("output/*Lband*.forPA_b128*"))
    filesS = np.sort(glob.glob("output/*Sband*.forPA_b128*"))
    npsr = len(filesL)
    for i in npsr:
        fit_RM([filesL[i], filesS[i]])
