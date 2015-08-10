import glob
import numpy as np

Lband_files = glob.glob("/nimrod1/GBT/Ter5/GUPPI/Lband_tscr/*tscr_ne*")
Sband_files = glob.glob("/nimrod1/GBT/Ter5/GUPPI/Sband_tscr/*tscr_ne*")
np.savetxt("starting_files_Lband.txt", np.sort(Lband_files), fmt="%s", delimiter=',')
np.savetxt("starting_files_Sband.txt", np.sort(Sband_files), fmt="%s", delimiter=',')
