import os
import subprocess
import glob

def correct_RM0(filename, RM0):
    """ Correct for preliminary rotation measure """
    call = 'pam -R %s -e rm_tscr -u ./output %s' %(RM0, filename)
    print(call)
    os.system(call)


def align_between_bands(filename):
    """ Line up between bands """
    out = subprocess.check_output(['psrstat', '-c', 'nbin', filename])
    out2 = out.split('=')[1]
    nbins = out2.split('\n')[0]
    filename_nodir = filename.split('/')[1]
    psr = filename_nodir.split('_')[0]
    direc = '/nimrod1/GBT/Ter5/GUPPI/PSRs/templates/'
    template = direc + '%s_%s_gaussians.template' %(psr, nbins)
    out = subprocess.check_output(['pat', '-R', '-TF', '-s', template, filename])
    rotateby = out.split(' ')[3]
    command = "pam -r %s -e autorot -u ./output %s" %(rotateby, filename)
    print(command)
    os.system(command)


def bin(filename):
    """ Bin the data to prepare it for fitting """
    call = "pam --setnbin 64 --setnchn 8 -e forPA_b64 -u ./output %s" %filename
    print(call)
    os.system(call)

    call = "pam --setnbin 128 --setnchn 8 -e forPA_b128 -u ./output %s" %filename
    print(call)
    os.system(call)

    call = "pam --setnbin 256 --setnchn 8 -e forPA_b256 -u ./output %s" %filename
    print(call)
    os.system(call)


def run(filename, RM0):
    correct_RM0(filename, RM0)
    filename_short = (filename.split('/')[-1]).split('.')[0]
    rm_corr = "output/" + filename_short + ".rm_tscr"
    align_between_bands(rm_corr)
    autorot = "output/" + filename_short + ".autorot"
    bin(autorot)
