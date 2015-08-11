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
    os.system("pam -r %s -e autorot -u ./output %s" %(rotateby, filename))


def bin(filename):
    """ Bin the data to prepare it for fitting """
    call = "pam --setnbin 64 --setnchn 8 -e forPA_b64 -u ./output %s" %filename
    print call
    os.system(call)

    call = "pam --setnbin 128 --setnchn 8 -e forPA_b128 -u ./output %s" %filename
    print call
    os.system(call)

    call = "pam --setnbin 256 --setnchn 8 -e forPA_b256 -u ./output %s" %filename
    print call
    os.system(call)


def run(filename, RM0):
    correct_RM0(filename, RM0)
    rm_corr = glob.glob("output/*.rm_tscr")
    for filename in rm_corr:
        align_between_bands(filename)
    autorot = glob.glob("output/*.autorot")
    for filename in autorot:
        bin(filename)
