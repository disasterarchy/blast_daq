import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt

# Data collection setup
RATE = 250
SAMPLES = 1000

# Create the I2C bus with a fast frequency
i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)

# ADC Configuration
ads.mode = Mode.CONTINUOUS
ads.data_rate = RATE

data = [None]*SAMPLES
data1 = [None]*SAMPLES
data2 = [None]*SAMPLES

start = time.monotonic()

# Read the same channel over and over
for i in range(SAMPLES):
    data[i] = chan0.voltage
    data1[i] = chan1.voltage
    data2[i] = chan2.voltage
    
end = time.monotonic()
total_time = end - start

print("Time of capture: {}s".format(total_time))
print("Sample rate requested={} actual={}".format(RATE, SAMPLES / total_time))
plt.plot(np.arange(0,1000), data, 'ro')
plt.plot(np.arange(0,1000), data1, 'bo')
plt.plot(np.arange(0,1000), data2, 'go')

plt.show()