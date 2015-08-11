import os
import numpy as np
import make_starting_file_list
import munge_data

# create list of starting files
make_starting_file_list.run()

# for each file in the list, generate a .forPA file used in fitting
starting_files = np.loadtxt("starting_files.txt", dtype=str, delimiter=',')
for filename in starting_files.flatten():
    munge_data.run(filename, 180) # supply the starting guess for RM
