import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt

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

plt.plot(arr[:,0],arr[:,1], 'bo',label='Reference')
plt.plot(arr[:,0],arr[:,2], 'yo', label = 'Active1')
plt.plot(arr[:,0],arr[:,3], 'go', label = 'Active2')
plt.plot(arr[:,0],arr[:,4], 'r-', label  = 'Lamp')
plt.legend()
plt.show()