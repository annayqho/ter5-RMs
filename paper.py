import os
import numpy as np
import glob
import make_starting_file_list
import munge_data
import read_data
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

# get data
filesL = np.sort(glob.glob("output/*Lband*.forPA_b128"))
filesS = np.sort(glob.glob("output/*Sband*.forPA_b128"))
npsr = len(filesL)
for i in range(npsr):
    pair = [filesL[i], filesS[i]]
    print(pair)
    RM0 = read_data.get_fileRM(pair[0])
    lsquareds, PAs, PAerrs = read_data.get_data(pair) # (nbin, nband, nchan)

# get new RM 
out = calc_params.run_with_offsets(lsquareds, PAs, PAerrs)
dRM, dRMerr, b0, b0err, db, dberr, chisq = out

calc_params.run_with_offset(lsquareds, PAs, PAerrs)
dRM, dRMerr, b0, b0err, db, dberr, chisq = out

calc_params.run_with_no_offset(lsquareds, PAs, PAerrs)
dRM, dRMerr, b0, b0err, chisq = out

RM = RM0 + dRM
