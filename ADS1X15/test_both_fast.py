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

GPIO.setmode(GPIO.BCM)
GPIO.setup(12,GPIO.OUT)
p = GPIO.PWM(12,4)
p.start(50.0)


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
chan0 = AnalogIn(ads1015, ADS0.P0)
chan1 = AnalogIn(ads1015, ADS0.P1)
chan2 = AnalogIn(ads1015, ADS0.P2)
chan3 = AnalogIn(ads1015, ADS0.P3)

chanB0 = AnalogIn(ads1115, ADS1.P0)
chanB1 = AnalogIn(ads1115, ADS1.P1)
chanB2 = AnalogIn(ads1115, ADS1.P2)
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
    vv =chanB0.voltage
    tV = chanB3.voltage
    return 100*(vv/0.0171), tV

def Run(SAMPLES, chan=True, chanB=False):
    arr = np.zeros((SAMPLES,5))
    arrB= np.zeros((SAMPLES,5))

    start = time.monotonic()

    # Read the same channel over and over
    for x in range(SAMPLES):
        dt = time.monotonic() - start
        if chan:
            arr[x] = [dt, chan0.voltage, chan1.voltage, chan2.voltage, chan3.voltage]
        if chanB:
            arrB[x] = [dt, chanB0.voltage, chanB1.voltage, chanB2.voltage, chanB3.voltage]
        
    end = time.monotonic()
    total_time = end - start

    print("Time of capture: {}s".format(total_time))
    print("Sample rate requested={} actual={}".format(RATE, SAMPLES / total_time))
    
    if chan:
        plt.plot(arr[:,0],arr[:,1], 'bo', label="0-Ref") #Reference
        plt.plot(arr[:,0],arr[:,2], 'go', label="1-Act1") #Active1
        plt.plot(arr[:,0],arr[:,3], 'mo', label="2-Act2") #Active2
        plt.plot(arr[:,0],arr[:,4], 'ro', label="3-Lamp") #Lamp
        plt.legend()
        plt.show()
    
    if chanB:
        plt.plot(arrB[:,0],arrB[:,1], 'bo', label="0-Ref") #Reference
        plt.plot(arrB[:,0],arrB[:,2], 'go', label="1-Act1") #Active1
        plt.plot(arrB[:,0],arrB[:,3], 'mo', label="2-Act2") #Active2
        plt.plot(arrB[:,0],arrB[:,4], 'ro', label="3-Lamp") #Lamp
        plt.legend()
        plt.show()
    
    return arr, arrB
    
def RunCont():
    while True:
        print(chan0.voltage)
        time.sleep(1.0)
