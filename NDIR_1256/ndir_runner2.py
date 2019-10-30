#!/usr/bin/python
# -*- coding:utf-8 -*-

import pandas as pd
import time
import ADS1256
import RPi.GPIO as GPIO
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
from scipy.ndimage import median_filter

samples = 300
start = datetime.now()
arr = np.zeros((samples,5))
pkx  =0

col= ['mnRef','mxRef','mnAct1','mxAct1', 'mnAct2', 'mxAct2', 'PkPkRef', 'PkPk1', 'PkPk2', 'Temp', 'CO2', 'CH4']
df = pd.DataFrame(np.array([[0],[0],[0],[0], [0],[0],[0],[0], [0], [0], [0],[0]]).transpose(),index = [0], columns=col)
cyclstart = datetime.now()

def Process(arr, df):
    
    dvalues = {}
    dvalues['time'] = datetime.now()
    filtered = median_filter(arr[:,1],7)
    dvalues['mnRef'] = np.min(filtered)
    dvalues['mxRef'] = np.max(filtered)
    
    filtered = median_filter(arr[:,2],7)
    dvalues['mnAct1'] = np.min(filtered)
    dvalues['mxAct1'] = np.max(filtered)
    
    filtered = median_filter(arr[:,3],7)
    dvalues['mnAct2'] = np.min(filtered)
    dvalues['mxAct2'] = np.max(filtered)
    
    last = df.shape[0]
    if last > 2:
        dvalues['PkPkRef'] = ((dvalues['mxRef']-dvalues['mnRef']) + (df.iloc[-1]['mxRef']-dvalues['mnRef']))/2.0
        dvalues['PkPk1'] = ((dvalues['mxAct1']-dvalues['mnAct1']) + (df.iloc[-1]['mxAct1']-dvalues['mnAct1']))/2.0
        dvalues['PkPk2'] = ((dvalues['mxAct2']-dvalues['mnAct2']) + (df.iloc[-1]['mxAct2']-dvalues['mnAct2']))/2.0
    
    else:
        dvalues['PkPkRef'] = dvalues['mxRef']-dvalues['mnRef']
        dvalues['PkPk1'] = dvalues['mxAct1']-dvalues['mnAct1']
        dvalues['PkPk2'] = dvalues['mxAct2']-dvalues['mnAct2']
        
    end = datetime.now()
    elapsed = end - cyclstart
    SPS = arr.shape[0]/elapsed.total_seconds()
    print("Arr shape: %d  Time: %5.2f  SPS: %5.2f" % (arr.shape[0], elapsed.total_seconds(), SPS))
    
    dff = df.append(dvalues, ignore_index=True)
    dtt = end-dvalues['time'] 
    print(dtt.total_seconds())
    print(dvalues)
    return dff
#try:
if True:
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
    y = 0
    x= 0
    
    while x<300:
        dt = datetime.now() - start
        arr[x] = [dt.total_seconds(),
                  ADC.ADS1256_GetChannalValue(0)*5.0/0x7fffff,
                  ADC.ADS1256_GetChannalValue(1)*5.0/0x7fffff,
                  ADC.ADS1256_GetChannalValue(2)*5.0/0x7fffff,
                  22]  #TODO replace with Temperature measurement
        x+=1
        if dt.total_seconds() > 0.105:
            stt = datetime.now()
            dd = np.diff(arr[x-10:x,0])*np.array([[1],[1],[1]])
            if np.max(np.diff(arr[x-10:x,1:4],axis=0)/dd.transpose()) < -0.02:
            #We are going downhill  do the processing!
                y+=1
                name = 'data/' + str(y) + 'arr.csv'
                np.savetxt(name,arr[:x])
                df = Process(arr[:x],df)
                start = datetime.now() 
                arr = np.zeros((samples,5))
                x=0
                dtt = datetime.now()-stt
                print('New Cycle', dtt.total_seconds())
                cyclstart = datetime.now()


    dt = datetime.now()-start
    sps =samples/dt.total_seconds()
    print("Total Time: %5.2f" % dt.total_seconds())
    print("SPS: %5.2f" % sps)
    plt.figure()
    plt.plot(arr[:,0],arr[:,1], 'bo') #Reference
    plt.plot(arr[:,0],arr[:,2], 'go') #Active1
    plt.plot(arr[:,0],arr[:,3], 'mo') #Active2
    plt.plot(arr[:,0],arr[:,4], 'r-') #Lamp
    plt.show()
    
    grarr = np.gradient(arr[:,0])
    plt.plot(arr[:,0],grarr)
    plt.show()
    
else:
#except:
    GPIO.cleanup()
    print ("\r\nProgram end     ")
    exit()
