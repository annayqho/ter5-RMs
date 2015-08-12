# Uses a Gaussian fit to data to find the minimum
from numpy import *
from pylab import *
from scipy import optimize

class Parameter:
    def __init__(self, value):
        self.value = value

    def set(self, value):
        self.value = value

    def __call__(self):
        return self.value

def fit(function, parameters, y, x):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)

    if x is None: x = arange(y.shape[0])
    p = [param() for param in parameters]
    return optimize.leastsq(f,p, full_output=1)

def findshift(psr, shifts, chisqs):
    # Gaussian Fit
    chisqs = array(chisqs)

    mu = Parameter(0.01)
    sigma = Parameter(0.01)
    height = Parameter(2)
    a = Parameter(1)

    # Define the function to be fitted
    def f(x): return height() + a() * exp(-((x-mu())/sigma())**2)

    out = fit(f, [mu, sigma, height, a], chisqs, shifts)
    p = out[0]
    mu = p[0]
    sigma = p[1]
    height = p[2]
    a = p[3]

    min_shift = mu
    min_chisq = height+a    

    x = linspace(min(shifts), max(shifts), 100)
    gaussian = height + a * exp(-((x-mu)/sigma)**2)

    #scatter(shifts, chisqs, marker='o', c='red')
    #plot(x, gaussian, c='blue')
    #set_title('Ter5%s' %psr)
    #savefig('Ter5%s_findshift.png' %psr)

    return min_shift, min_chisq, x, gaussian

if __name__ == "__main__":
    readin = open('shiftresults.txt', 'r')
    lines = readin.readlines()
    chisqs = []
    for line in lines:
        chisq = float(line.split(' ')[2].strip('\n'))
        chisqs.append(chisq)
    min_shift, min_chisq = findshift('C', chisqs)
