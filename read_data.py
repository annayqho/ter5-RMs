import globalfit as g

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

