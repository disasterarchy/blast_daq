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
from NDIR_calc import *
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from scipy import signal
from o2_helper import GetO2
import cProfile, pstats, io
from pstats import SortKey
import sys
import os

prAr = []
DF = pd.DataFrame()
msg ={}
path = os.getcwd()

GPIO.setmode(GPIO.BCM)
GPIO.setup(12,GPIO.OUT)
p = GPIO.PWM(12,4)
p.start(50.0)

def RevPlots2(istart,iend):
    for i in range(istart,iend):
        arr = np.genfromtxt('data/' + str(i) + 'arr.csv')
        plt.plot(arr[:,0],arr[:,1], 'bo', label="0-Ref") #Reference
        plt.plot(arr[:,0],arr[:,2], 'go', label="1-Act1") #Active1
        plt.plot(arr[:,0],arr[:,3], 'mo', label="2-Act2") #Active2
        plt.legend()
        plt.show()    

#Review Plots
def ReviewPlots(col, istart,iend):
    for i in range(istart,iend):
        arr = np.genfromtxt('data/' + str(i) + 'arr.csv')
        plt.plot(arr[:,0], arr[:,col], 'bo', label= 'Raw Data')
        plt.plot(arr[:,0], median_filter(arr[:,col],5), label = 'median5')
        b, a = signal.butter(3, 50, fs=900)
        y50 = signal.filtfilt(b,a, arr[:,col])
        plt.plot(arr[:,0], y50, label = '50hz LP Butter')
        b, a = signal.butter(3, 100, fs=900)
        y100 = signal.filtfilt(b,a, arr[:,col])
        plt.plot(arr[:,0], y100, label = '100hz LP Butter')
        b, a = signal.butter(3, 30, fs=900)
        y30 = signal.filtfilt(b,a, arr[:,col])
        plt.plot(arr[:,0], y30, label = '30hz LP Butter')
        
        idxmax=np.argmax(arr[:,col])
        if max(abs(np.diff(arr[idxmax-1:idxmax+2,col])/np.diff(arr[idxmax-1:idxmax+2,0]))) > 10:
            mmax = np.max(median_filter(arr[idxmax-20::,col],5))
        else:
            mmax = arr[idxmax,col]
        
        idxmin=np.argmin(arr[:,col])
        if max(abs(np.diff(arr[idxmin-1:idxmin+2,col])/np.diff(arr[idxmin-1:idxmin+2,0]))) > 10:
            mmin = np.min(median_filter(arr[0:idxmin+20,col],5))
        else:
            mmin = arr[idxmin,col]
        
        mm = np.array([[arr[idxmin,0],mmin],[arr[idxmax,0],mmax]])
        plt.plot(mm[:,0], mm[:,1],'ro')
        plt.legend()
        plt.show()

def GetMinMax(arr,col):
    #idxmax=np.argmax(arr[:,col])
    mmax = np.max(median_filter(arr[:,col],5))
    mmin = np.min(median_filter(arr[:,col],5))
#    if max(abs(np.diff(arr[idxmax-1:idxmax+2,col])/np.diff(arr[idxmax-1:idxmax+2,0]))) > 10:
#        mmax = np.max(median_filter(arr[idxmax-20::,col],5))
#    else:
#        mmax = arr[idxmax,col]
#    
#    idxmin=np.argmin(arr[:,col])
#    if max(abs(np.diff(arr[idxmin-1:idxmin+2,col])/np.diff(arr[idxmin-1:idxmin+2,0]))) > 10:
#        mmin = np.min(median_filter(arr[0:idxmin+20,col],5))
#    else:
#        mmin = arr[idxmin,col]
    
    return mmin, mmax

#Process a set of data points
def Process(arr, df, y):
    dv = {}
    dv['time'] = datetime.now()
    dv['mnRef'], dv['mxRef'] = GetMinMax(arr,1)
    dv['mnAct1'], dv['mxAct1'] = GetMinMax(arr,2)
    dv['mnAct2'], dv['mxAct2'] = GetMinMax(arr,3)
    last = df.shape[0]
    if last > 2:
        dv['PkPkRef'] = ((dv['mxRef']-dv['mnRef']) + (df.iloc[-1]['mxRef']-dv['mnRef']))/2.0
        dv['PkPk1'] = ((dv['mxAct1']-dv['mnAct1']) + (df.iloc[-1]['mxAct1']-dv['mnAct1']))/2.0
        dv['PkPk2'] = ((dv['mxAct2']-dv['mnAct2']) + (df.iloc[-1]['mxAct2']-dv['mnAct2']))/2.0
    
    else:
        dv['PkPkRef'] = dv['mxRef']-dv['mnRef']
        dv['PkPk1'] = dv['mxAct1']-dv['mnAct1']
        dv['PkPk2'] = dv['mxAct2']-dv['mnAct2']
    dv['Temperature'] = np.mean(arr[:,4])
    dv['CO2pct'] = NDIR('CO2',dv['PkPk2'],dv['PkPkRef'],dv['Temperature'])
    dv['CH4pct'] = NDIR('CH4',dv['PkPk1'],dv['PkPkRef'],dv['Temperature'])
    dv['O2'] = max(GetO2(),-1)
    end = datetime.now()
    elapsed = arr[-1,0]
    SPS = arr.shape[0]/elapsed
    time.sleep(0.01)   
    dff = df.append(dv, ignore_index=True)
    dtt = end-dv['time']
    #print("CO2: %5.2f  CH4: %5.2f" % (dv['CO2pct'], dv['CH4pct']))
    #print(elapsed)
    #print("O2: %5.1f CO2: %5.1f CH4: %5.1f " % dv['O2'], dv[PkPk2)
    print(y, "Time: %5.2f  Process: %5.3f SPS: %5.1f  O2: %5.1f CO2: %5.1f  CH4: %5.1f PkPkRef: %5.3f PkPkCH4: %5.3f PkPkCO2: %5.3f " % (elapsed, dtt.total_seconds(), SPS, dv['O2'], dv['CO2pct'], dv['CH4pct'], dv['PkPkRef'], dv['PkPk1'], dv['PkPk2'])) 
    
    return dff
#try:

def Run(nn, testname):
    pth = path + "/" + str(testname)
    pthdata = path + "/" + str(testname) + "/data"
    os.mkdir(pth)
    os.mkdir(pthdata)
    prAr = []
    DF = pd.DataFrame()
    pr = cProfile.Profile()
    pr.enablGPIO.setmode(GPIO.BCM)
GPIO.setup(12,GPIO.OUT)
p = GPIO.PWM(12,4)
p.start(50.0)e()
    samples = 300
    ostart = datetime.now()
    arr = np.zeros((samples,5))
    pkx  =0

    df = pd.DataFrame()
    cyclstart = datetime.now()
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
    y = 0
    x= 0
    z=0
    start = datetime.now()
    
    while y<nn:
        z=0
        try:
            dt = datetime.now() - start
            arr[x] = [dt.total_seconds(),
                      ADC.ADS1256_GetChannalValue(0)*5.0/0x7fffff,
                      ADC.ADS1256_GetChannalValue(1)*5.0/0x7fffff,
                      ADC.ADS1256_GetChannalValue(2)*5.0/0x7fffff,
                      22]  #TODO replace with Temperature measurement
            x+=1
            if x > 299:
                ADC = ADS1256.ADS1256()
                ADC.ADS1256_init()
                x=0
            if dt.total_seconds() > 0.180:
                stt = datetime.now()
                if np.median(np.diff(arr[x-9:x,1])/np.diff(arr[x-9:x,0])) < -1.0:
                #We are going downhill  do the processing!
                    y+=1
                    name = pth + "/" + 'data/' + str(y) + 'arr.csv'
                    np.savetxt(name,arr[:x])
                    df.to_csv("out" + ostart.isoformat() +'.csv')
                    df = Process(arr[:x],df,y)
                    start = datetime.now() 
                    arr = np.zeros((samples,5))
                    x=0
                    dtt = datetime.now()-stt
                    cyclstart = datetime.now()
            pr.disable()
            prAr.append(pr)
        except Exception as exx:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            msg[str(y) +'-'  + str(x) + '-' +str(z)] = [exx, exc_type, exc_obj, exc_tb]
            z +=1
            #print(type(exx))
            #print(exx.args)
            #print(exx)
            
            pr.disable()
            prAr.append(pr)
            df.to_csv(pth + "/out" + ostart.isoformat() +'.csv')
            DF = df
            
    #plt.plot(df['time'], df['CO2pct'], label = 'CO2')
    #plt.plot(df['time'], df['CH4pct'], label = 'CH4' )
    #plt.legend()
    #plt.show()
    print("done")
    df.to_csv(pth + "/out" + ostart.isoformat() +'.csv')
    return df
if False:
#except:
    GPIO.cleanup()
    print ("\r\nProgram end     ")
    exit()

#sos = signal.butter(1000,50, 'hp', fs = 1000, output='sos')
#filtered = signal.sosfilt(sos,sig)
if __name__ == '__main__':
    dff = Run(100,'test'+datetime.now().isoformat()[:-7])
#    pr = cProfile.Profile()
#    pr.enable()
#    dff = Run(100)
#    pr.disable()
#    s = io.StringIO()
#    sortby = SortKey.CUMULATIVE
#    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#    ps.print_stats()
#    print(s.getvalue())