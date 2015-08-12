import os
import numpy as np
import make_starting_file_list
import munge_data
import calc_params 

# create list of starting files
make_starting_file_list.run()

# for each file in the list, generate a .forPA file used in fitting
starting_files = np.loadtxt("starting_files.txt", dtype=str, delimiter=',')
for filename in starting_files.flatten():
    psr = (filename.split('/')[-1]).split('_')[0]
    if psr == 'Ter5D':
        munge_data.run(filename, 220) # Ter5D has a much higher RM
    else:
        munge_data.run(filename, 180) # supply the avg cluster val as RM guess 

# get new RM 
calc_params.run()
