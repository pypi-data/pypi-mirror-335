import eyes17.eyes
p = eyes17.eyes.open()

from matplotlib import pyplot as plt
import time
from scipy.optimize import leastsq
import numpy as np

#-------------------------- Exponential Fit ----------------------------------------
def exp_erf(p,y,x):
	return y - p[0] * np.exp(p[1]*x) + p[2]

def exp_eval(x,p):
	return p[0] * np.exp(p[1]*x)  -p[2]

def fit_exp(xlist, ylist):
	size = len(xlist)
	xa = np.array(xlist, dtype=float)
	ya = np.array(ylist, dtype=float)
	maxy = max(ya)
	halfmaxy = maxy / 2.0
	halftime = 1.0
	for k in range(size):
		if abs(ya[k] - halfmaxy) < halfmaxy/100:
			halftime = xa[k]
			break 
	par = [maxy, -halftime,0] 					# Amp, decay, offset
	plsq = leastsq(exp_erf, par,args=(ya,xa))
	if plsq[1] > 4:
		return None
	yfit = exp_eval(xa, plsq[0])
	return yfit,plsq[0]



# OD1 to HIGH
p.set_state(OD1=1)			
#Wait for full charging
time.sleep(.5) 
# Set OD1 Low, and capture decay curve
t,v = p.capture_action('A1', 600, 5, 'SET_LOW')
t = t/1e3 # Convert time from mS into seconds

yfit, parameters = fit_exp(t,v)

#Original data
plt.plot(t,v,linewidth = 2, color = 'black')

#Fitted data overlay
fig = plt.plot(t,yfit,linewidth = 2, color = 'red')

plt.title(f'Amp : {parameters[0]}, lambda: {parameters[1]}, RC:{np.abs(1000./parameters[1]):.3} mS')

plt.show()
