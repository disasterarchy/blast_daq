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
    dt = datetime.now()-start
    arr[x] = [dt.total_seconds(), chan.voltage, chan1.voltage, chan2.voltage, 0.0]
    #print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
    #time.sleep(0.5)

dt = datetime.now()-start
print("Samples per second %5.2f" % (samples/dt.total_seconds()))
start = datetime.now()

import numpy as np
from scipy.optimize import leastsq

#N = 1000 # number of data points
#t = np.linspace(0, 4*np.pi, N)
#f = 1.15247 # Optional!! Advised not to use
#data = 3.0*np.sin(f*t+0.001) + 0.5 + np.random.randn(N) # create artificial data with noise

N = len(arr[:,0])
t = arr[:,0]
data = arr[:,2]

guess_mean = np.mean(data)
guess_std = 3*np.std(data)/(2**0.5)/(2**0.5)
guess_phase = 0
guess_freq = 4*2*np.math.pi
guess_amp = np.max(data)-np.min(data)

fine_t = np.arange(0,max(t),0.01)

# we'll use this to plot our first estimate. This might already be good enough for you
data_first_guess = guess_std*np.sin(guess_freq*fine_t+guess_phase) + guess_mean

# Define the function to optimize, in this case, we want to minimize the difference
# between the actual data and our "guessed" parameters
optimize_func = lambda x: x[0]*np.sin(x[1]*t+x[2]) + x[3] - data
est_amp, est_freq, est_phase, est_mean = leastsq(optimize_func, [guess_amp, guess_freq, guess_phase, guess_mean])[0]

# recreate the fitted curve using the optimized parameters
data_fit = est_amp*np.sin(est_freq*t+est_phase) + est_mean

# recreate the fitted curve using the optimized parameters
end = datetime.now()
dt = end-start
print(dt.total_seconds())

fine_t = np.arange(0,max(t),0.01)
data_fit=est_amp*np.sin(est_freq*fine_t+est_phase)+est_mean

plt.plot(t, data, '.')
plt.plot(fine_t, data_first_guess, label='first guess')
plt.plot(fine_t, data_fit, label='after fitting')
plt.legend()
plt.show()







plt.plot(arr[:,0],arr[:,1], 'bo',label='Reference')
plt.plot(arr[:,0],arr[:,2], 'yo', label = 'Active1')
plt.plot(arr[:,0],arr[:,3], 'go', label = 'Active2')
plt.plot(arr[:,0],arr[:,4], 'r-', label  = 'Lamp')
plt.legend()
plt.show()
