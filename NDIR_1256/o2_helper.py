import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS1
import adafruit_ads1x15.ads1015 as ADS0
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt

import RPi.GPIO as GPIO

# Data collection setup
RATE = 250
RATEB = 250
SAMPLES = 1000

# Create the I2C bus with a fast frequency
i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)

# Create the ADC object using the I2C bus

ads1015 = ADS0.ADS1015(i2c)
ads1115 = ADS1.ADS1115(i2c, address=0x4a)

# Create single-ended input on channel 0
#chan0 = AnalogIn(ads1015, ADS0.P0)
#chan1 = AnalogIn(ads1015, ADS0.P1)
#chan2 = AnalogIn(ads1015, ADS0.P2)
chan3 = AnalogIn(ads1015, ADS0.P3)

#chanB0 = AnalogIn(ads1115, ADS1.P0)
#chanB1 = AnalogIn(ads1115, ADS1.P1)
#chanB2 = AnalogIn(ads1115, ADS1.P2)
chanB3 = AnalogIn(ads1115, ADS1.P3)

# ADC Configuration
ads1115.mode = Mode.SINGLE
ads1115.data_rate = RATEB
ads1115.gain = 16

ads1015.mode = Mode.SINGLE
ads1015.data_rate = RATE
ads1015.gain = 1


def GetO2():
    vv =chan0.voltage
    return 100*(vv/0.0171)

def GetO2_Temp():
    vv =chanB3.voltage
    tv = chan3.voltage
    Temp = 107.3158 - 60.9514*tv + 16.01841*tv**2 - 1.93628 * tv**3
    return vv, Temp

def GetO2():
    vv =chan0.voltage
    return 20.95*(vv/0.0171)

def Run(SAMPLES):
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
    #plt.plot(np.arange(0,1000), data1, 'bo')
    #plt.plot(np.arange(0,1000), data2, 'go')

    plt.show()
def RunCont():
    while True:
        print(chan0.voltage)
        time.sleep(1.0)
