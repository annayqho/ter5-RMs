import glob
import numpy as np

def run():
    Lband_files = glob.glob("/nimrod1/GBT/Ter5/GUPPI/Lband_tscr/*summed.tscr")
    Sband_files = glob.glob("/nimrod1/GBT/Ter5/GUPPI/Sband_tscr/*summed.tscr")
    np.savetxt("starting_files_Lband.txt", np.sort(Lband_files), fmt="%s", delimiter=',')
    np.savetxt("starting_files_Sband.txt", np.sort(Sband_files), fmt="%s", delimiter=',')

if __name__ == '__main__':
    run()
