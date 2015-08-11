import os
import subprocess
import glob

def correct_RM0(filename, RM0):
    """ Correct for preliminary rotation measure """
    call = 'pam -R %s -e rm_tscr -u ./output %s' %(RM0, filename)
    print(call)
    os.system(call)


def align_between_bands(psr):
    """ Line up between bands """
    for file in glob.glob('Ter5%s*.rm_tscr' %psr): # for each band,
        out = subprocess.check_output(['psrstat', '-c', 'nbin', file])
        out2 = out.split('=')[1]
        nbins = out2.split('\n')[0]
        template = 'Ter5%s_%s_gaussians.template' %(psr, nbins)
        out = subprocess.check_output(['pat', '-R', '-TF', '-s', template, file])
        rotateby = out.split(' ')[3]
        os.system("pam -r %s -e autorot %s" %(rotateby, file))


def bin(psr):
    """ Bin the data to prepare it for fitting """
    call = "pam --setnbin 64 --setnchn 8 -e forPA_b64 Ter5%s*.autorot" %psr
    print call
    os.system(call)

    call = "pam --setnbin 128 --setnchn 8 -e forPA_b128 Ter5%s*.autorot" %psr
    print call
    os.system(call)

    call = "pam --setnbin 256 --setnchn 8 -e forPA_b256 Ter5%s*.autorot" %psr
    print call
    os.system(call)


def run(filename, RM0):
    correct_RM0(filename, RM0)
