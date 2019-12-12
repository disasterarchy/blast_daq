#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import ADS1256
import RPi.GPIO as GPIO
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
samples = 1000

GPIO.setmode(GPIO.BCM)
GPIO.setup(12,GPIO.OUT)
p = GPIO.PWM(12,4)
p.start(50.0)

arr = np.zeros((samples,5))

def doSample():
    start = datetime.now()
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()

    for x in range(0,samples):
        #ADC_Value = ADC.ADS1256_GetAll()
        dt = datetime.now() - start
        arr[x] = [dt.total_seconds(),
                  ADC.ADS1256_GetChannalValue(0)*5.0/0x7fffff,
                  ADC.ADS1256_GetChannalValue(1)*5.0/0x7fffff,
                  ADC.ADS1256_GetChannalValue(2)*5.0/0x7fffff,
                  ADC.ADS1256_GetChannalValue(3)*5.0/0x7fffff]
        #if ADC.ADS1256_GetChannalValue(0) > maxval:
            
        if x % 1000 == 1:
            tavg = arr[x,0]-arr[x-1000,0]
            print("Average Time: %5.4f " % tavg)
    dt = datetime.now()-start
    sps =samples/dt.total_seconds()
    print("Total Time: %5.2f" % dt.total_seconds())
    print("SPS: %5.2f" % sps)
    return arr
    
def endplots(arr):
    plt.plot(arr[:,0],arr[:,1], 'b-', label="0-Ref") #Reference
    plt.plot(arr[:,0],arr[:,2], 'go', label="1-Act1") #Active1
    plt.plot(arr[:,0],arr[:,3], 'mo', label="2-Act2") #Active2
    plt.plot(arr[:,0],arr[:,4], 'ro', label="3-Lamp") #Lamp
    plt.legend()
    plt.show()
    
    #grarr = np.gradient(arr[:,0])
    #plt.plot(arr[:,0],grarr)
    #plt.show()
    
    np.savetxt('out.csv', arr)
    
    #GPIO.cleanup()
    #print ("\r\nProgram end     ")
    #exit()
    
def doBoth(n=1):
    for i in range(0,n):
        arr = doSample()
        endplots(arr)
    
doBoth()

    
