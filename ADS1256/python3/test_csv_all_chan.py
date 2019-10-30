#!/usr/bin/python
# -*- coding:utf-8 -*-


import time
import ADS1256
import RPi.GPIO as GPIO
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
samples = 1000
start = datetime.now()
arr = np.zeros((samples,5))

#try:
if True:
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
            
        
        #print ("0 ADC = %lf"%(ADC_Value[0]*5.0/0x7fffff))
        #print ("1 ADC = %lf"%(ADC_Value[1]*5.0/0x7fffff))
        #print ("2 ADC = %lf"%(ADC_Value[2]*5.0/0x7fffff))
        #print ("3 ADC = %lf"%(ADC_Value[3]*5.0/0x7fffff))
        #print ("4 ADC = %lf"%(ADC_Value[4]*5.0/0x7fffff))
        #print ("5 ADC = %lf"%(ADC_Value[5]*5.0/0x7fffff))
        #print ("6 ADC = %lf"%(ADC_Value[6]*5.0/0x7fffff))
        #print ("7 ADC = %lf"%(ADC_Value[7]*5.0/0x7fffff))
        #print ("\33[9A")
    dt = datetime.now()-start
    sps =samples/dt.total_seconds()
    print("Total Time: %5.2f" % dt.total_seconds())
    print("SPS: %5.2f" % sps)
    plt.plot(arr[:,0],arr[:,1], 'bo') #Reference
    plt.plot(arr[:,0],arr[:,2], 'go') #Active1
    plt.plot(arr[:,0],arr[:,3], 'mo') #Active2
    plt.plot(arr[:,0],arr[:,4], 'r-') #Lamp
    plt.show()
    
    grarr = np.gradient(arr[:,0])
    plt.plot(arr[:,0],grarr)
    plt.show()
    
    np.savetxt('out.csv', arr)
else:
#except:
    GPIO.cleanup()
    print ("\r\nProgram end     ")
    exit()
