""" A set of diagnostic plots """

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


def diagnostic_bin_consistency(lsquareds, PAs, PAerrs, psr):
    """ Plot the RM calculated for each bin individually """ 
    bins, RM_all, RMerr_all, offset_all, offseterr_all = calc_RM_indbins(
        lsquareds, PAs, PAerrs, psr)
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

