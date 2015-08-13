import globalfit as g
import math_funcs as mf

def getPAs_singlebin(filename, b):
    """ Run the pdv command to extract PAs and PAerrors from a single bin """
    output = subprocess.check_output(
        ['pdv', '-j', 'R 0', '-b %s' %b, '-Z', '-A', '-L 3', filename])
    output_split = np.array(output.split())[14:]
    nrows = 8
    ncols = len(output_split)/nrows
    rows = output_split.reshape((nrows,ncols))
    freqs = rows[:,5].astype(float)
    lsquareds = np.array([math_funcs.ftolsquared(f) for f in freqs])
    PAerrs = rows[:,ncols-1].astype(float) * m.pi/180.
    PAerrs[PAerrs == 0] = 1e10 # ignore these data points in the fit
    # it's easier to handle the data when it's between 0 and pi  
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
        # Test for wrapping 
        flatl = ltemp.flatten()
        flatPA = PAtemp.flatten()
        flatPAerr = PAerrtemp.flatten()
        testPA = (flatPA + np.pi/2)%np.pi
        w = 1./flatPAerr**2
        if np.round(mf.std_w(testPA, w),5) < np.round(mf.std_w(flatPA, w),5):
            PAs[b,:,:] = (PAtemp + np.pi/2)%np.pi
        else:
            PAs[b,:,:] = PAtemp
        lsquareds[b,:,:] = ltemp
        PAerrs[b,:,:] = PAerrtemp
    return np.array(lsquareds), np.array(PAs), np.array(PAerrs)


def get_data(pair):
    """ Extract lsquareds, PAs, PAerrs from a pair of forPA files 

    Parameters
    ----------
    pair = [Lband_file, Sband_file]
    """
    nbands = len(pair)
    psr = pair[0].split('/')[1]
    psr = psr.split('_')[0]
    nbin = int(pair[0].split('_')[3][1:])
    print("getting data points")
    lsquareds, PAs, PAerrs = g.getPAs_allbins(pair, nbin)
    return lsquareds, PAs, PAerrs


def get_fileRM(filename):
    """ Read the RM from a file """
    out = subprocess.check_output(
        ['psrstat', '-c', 'rm', 'output/Ter5C_Lband_summed.forPA_b128'])
    return (out.split()[1]).split('=')[1]

