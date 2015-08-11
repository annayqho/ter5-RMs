import glob
import numpy as np

def run():
    Lband_files = glob.glob("/nimrod1/GBT/Ter5/GUPPI/Lband_tscr/*summed.tscr")
    Sband_files = glob.glob("/nimrod1/GBT/Ter5/GUPPI/Sband_tscr/*summed.tscr")
    allfiles = np.vstack((np.sort(Lband_files), np.sort(Sband_files)))
    np.save("starting_files", allfiles.T, delimiter=',', fmt='%s')

if __name__ == '__main__':
    run()
