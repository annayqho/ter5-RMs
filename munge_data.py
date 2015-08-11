""" Methods for preparing calibrated data for RM measurement """

import os
import subprocess
import numpy as np

def getnumbins(filename):
	command = "psrstat -c all:count %s" %filename
	print command
	output = subprocess.check_output(['psrstat', '-c', 'all:count', filename])
	numbins = (output.split('=')[1])[0:3]
	return numbins


def sum(pulsar):
	call = "psradd -o Ter5%s_Lband_summed_prelim.tscr -T -ip GUPPI_Ter5%s*aligned" %(pulsar, pulsar)
	os.system(call)
	print call
	call = "psradd -o Ter5%s_Lband_summed_prelim_old.tscr -T -ip GUPPI_Ter5%s_1[0,1,2]*aligned" %(pulsar, pulsar)
	print call
	os.system(call)


# Align using Gaussian template
def align_gaussian_template(filenames):
    for filename in filenames:
		numbins = getnumbins(filename)
		templatefile = "/nimrod1/GBT/Ter5/GUPPI/PSRs/templates/*%s*%s*.template" %(pulsar, numbins)
		command = "pat -R -TF -s %s %s" %(templatefile, filename)
		print command
		os.system(command)
		rotateby = raw_input("Amount to rotate by: ")
		command = "pam -r %s -e aligned %s" %(rotateby, filename)
		print command
		os.system(command)


# Uses Tim's code
def talign(pulsar, files, numbins):
	ephemerisfile = "/nimrod1/GBT/Ter5/GUPPI/PSRs/Ter5_130805_parfiles/*%s*" %pulsar
	for filename in files:
        	print "Filename: %s" %filename
                #command = "psrstat -c all:count %s" %filename
                #print command
                #os.system(command)
                #numbins = int(raw_input())
                #print "Number of bins: %s" %numbins
                templatefile = "/nimrod1/GBT/Ter5/GUPPI/PSRs/templates/*%s*%s*.template" %(pulsar, numbins)
                command = "python ppalign.py -d %s -t %s -E %s --talign --ext aligned" %(filename, templatefile, ephemerisfile)
                print command
                os.system(command)


def dedisperse(filename):
	act_on = filename
	call = "psrstat -c dm %s" %act_on
	print "Check if DMs are consistent!"
	print call
	os.system(call)
	# 1500 is a good frequency for this, because that's part of both L-band and S-band data.
	# So, any offsets won't be due to dedispersing to different frequencies. 
	call = "pam -e dd -D 'D 1500' %s" %act_on
	print call
	os.system(call)

		
def fscrunch(filename, numchan):
	act_on = filename
	call = "pam -e fscr --setnchn %s %s" %(numchan, filename)
	print call
	os.system(call) 


def put_new_ephemeris(filename, psr):
	pf = "/nimrod1/GBT/Ter5/GUPPI/parfiles/1748-2446%s.par" % psr
    	pp = parfile.psr_par(pf)
    	call = "nice pam -E %s -e zap_ne --update_dm %s" % (pf, filename)
    	#call = "nice pam -m -d %.7g GUPPI_Ter5%s*.calib_ne" % (pp.DM, psr)
    	print call
    	os.system(call)


def multiplyflux(files, factor):
	for filename in files:
		call = "pam --mult %s -m %s" %(factor, filename)
		print call
		os.system(call)


if __name__=='__main__':
    # Align profiles across days
    allfilesL = np.loadtxt("starting_files_Lband.txt", delimiter=',', dtype=str)
    allfilesS = np.loadtxt("starting_files_Sband.txt", delimiter=',', dtype=str)
    allfiles = np.concatenate((allfilesL, allfilesS)) 
    psrs = [a.split('_')[2] for a in allfiles] # ex. Ter5A
    
    # for isolated pulsars, align using the Gaussian template
	isolated_short = np.array(['C', 'D', 'F', 'G', 'H', 'K', 'L', 'R', 'S', 'T', 'aa',
                    'ab', 'ac', 'af', 'ag', 'ah'])
    isolated = np.array(['Ter5' + a for a in isolated_short])
    ind_isolated = np.array([np.where(psrs==a)[0] for a in isolated]).flatten()
	for filename in allfiles[ind_isolated]:
		align_gaussian_template(filename)
	
	psr = 'ae'
	nbin = '256'
	ext = 'fscr8_tscr2'
	band = 'Lband'
	Sbanddates = set(['100815', '120415'])
	#Lbanddates = set(['130107'])
	#Lbanddates = Lbanddates - Lbanddates2 
	files = []

	for date in Lbanddates:
		if date == "130407":
			filename = "Ter5%s_%s/GUPPI_Ter5%s_130407a_0001.%s" %(psr, band, psr, ext)
			files.append(filename)
                        filename = "Ter5%s_%s/GUPPI_Ter5%s_130407b_0001.%s" %(psr, band, psr, ext)
                        files.append(filename)
		elif date == "120411":
			filename = "Ter5%s_%s/GUPPI_Ter5%s_120411a_0001.%s" %(psr, band, psr, ext)
                        files.append(filename)
                        filename = "Ter5%s_%s/GUPPI_Ter5%s_120411b_0001.%s" %(psr, band, psr, ext)
                        files.append(filename)
#		elif date == "130417":
 #                       file = "Ter5%s_%s/GUPPI_Ter5%s_130417_0001.%s" %(psr, band, psr, ext)
  #                      files.append(file)
   #                     file = "Ter5%s_%s/GUPPI_Ter5%s_130417a_0001.%s" %(psr, band, psr, ext)
    #                    files.append(file)
		else:
                        filename = "Ter5%s_%s/GUPPI_Ter5%s_%s_0001.%s" %(psr, band, psr, date, ext)
			files.append(filename)
		
	talign(psr, files, nbin)
	
	#for psr in PSRs:
	#	remove = set(['100501'])
		#file = "GUPPI*Ter5%s*.dd" %psr
		#numchan = '8'
		#fscrunch(file, numchan)
	#	for date in dates:
	#		filename = "GUPPI_Ter5%s*%s*.fscr" %(psr, date)
	#		files.append(filename)

	#multiplyflux(files, '20.0')
			
