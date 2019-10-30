import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
import numpy, scipy.optimize

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

ads.data_rate = 860

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)
samples = 250

print("{:>5}\t{:>5}".format('raw', 'v'))
start = datetime.now()
arr = np.zeros((samples,5))

for x in range(0,samples):
    dt = start - datetime.now()
    arr[x] = [dt.total_seconds(), chan.voltage, chan1.voltage, chan2.voltage, chan3.voltage]
    #print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
    #time.sleep(0.5)

start = datetime.now()
def fit_sin(tt, yy):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
    tt = numpy.array(tt)
    yy = numpy.array(yy)
    ff = numpy.fft.fftfreq(len(tt), (tt[1]-tt[0]))   # assume uniform spacing
    Fyy = abs(numpy.fft.fft(yy))
    guess_freq = abs(ff[numpy.argmax(Fyy[1:])+1])   # excluding the zero frequency "peak", which is related to offset
    guess_amp = numpy.std(yy) * 2.**0.5
    guess_offset = numpy.mean(yy)
    guess = numpy.array([guess_amp, 2.*numpy.pi*guess_freq, 0., guess_offset])

    def sinfunc(t, A, w, p, c):  return A * numpy.sin(w*t + p) + c
    popt, pcov = scipy.optimize.curve_fit(sinfunc, tt, yy, p0=guess)
    A, w, p, c = popt
    f = w/(2.*numpy.pi)
    fitfunc = lambda t: A * numpy.sin(w*t + p) + c
    return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1./f, "fitfunc": fitfunc, "maxcov": numpy.max(pcov), "rawres": (guess,popt,pcov)}


N, amp, omega, phase, offset, noise = 500, 1., 2., .5, 4., 3
#N, amp, omega, phase, offset, noise = 50, 1., .4, .5, 4., .2
#N, amp, omega, phase, offset, noise = 200, 1., 20, .5, 4., 1
#tt = numpy.linspace(0, 10, N)

tt = arr[:,0]
yy = arr[:,1]


end = datetime.now()
dt = end-start
print(dt.total_seconds())
res = fit_sin(tt, yy)
print( "Amplitude=%(amp)s, Angular freq.=%(omega)s, phase=%(phase)s, offset=%(offset)s, Max. Cov.=%(maxcov)s" % res )

plt.plot(tt, yy, "-k", label="y", linewidth=2)
plt.plot(tt, res["fitfunc"](tt), "r-", label="y fit curve", linewidth=2)
plt.legend(loc="best")
plt.show()



plt.plot(arr[:,0],arr[:,1], 'bo',label='Reference')
plt.plot(arr[:,0],arr[:,2], 'yo', label = 'Active1')
plt.plot(arr[:,0],arr[:,3], 'go', label = 'Active2')
plt.plot(arr[:,0],arr[:,4], 'r-', label  = 'Lamp')
plt.legend()
plt.show()
