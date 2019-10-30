import numpy as np
import matplotlib.pyplot as plt
from Data_analysis import *
import scipy.ndimage as spy

## NDIR_Parser
## Robert Kennedy 7/22/2019 for plotting all data from NDIR Sensor and calibrating
## Requires file name, directory, extension (nominally .csv)
## Purpose: plots quantities of interest and calibrate sensor


def NDIR_calib(gas,Channel,ref_calib,reference,zero_voltage,span_conc,span_voltage,Temperature,Temp_cal): ## NDIR Calibration
    
    if gas=='CO2':
        a=0.106
        n=0.542
        alpha=0.000586
        beta=-0.088
    elif gas=='CH4':
        a=0.015
        n=0.464
        alpha=0.000438
        beta=-1.636
    else:
        error='Gas Not Here'
        return error
    Tcal=Temp_cal+273.15
    T=Temperature+273.15
    Zero=zero_voltage/ref_calib
    Span=(1-span_voltage/(Zero*ref_calib))/(1-np.exp(-a*span_conc**n))
    ratio=Channel/(Zero*reference)*(1+alpha*(T-Tcal))
    Span=Span+(beta*(T-Tcal)/Tcal)
    calibrated_data=np.zeros(len(Span))
    for i in range(len(Span)):
        if (-np.log(1-((1-ratio[i])/Span[i]))/a)>0:
            calibrated_data[i]=(-np.log(1-((1-ratio[i])/Span[i]))/a)**(1/n)

    return calibrated_data


## Inputs

file_name_calib='NDIR Calib 7-19-19'
file_name_target='8_14_2019 235 PM_Eriks Computer'
file_name_save='NDIR Tesvolt module 8_14_2019 235PM_Eriks Computer calibrated'
Save=True

extension='.csv'
source_dir=r'C:\Users\rkenn\Nextcloud\Infiltrator\Documents'
save_dir=r'C:\Users\rkenn\Nextcloud\Infiltrator\Documents'

CO2=5.63#39.77
CH4=1#18.62
CO2_times=[1680,1880] #2100,2200
CH4_times=[2350,2413] #5300,5350
zero_voltage_time=2430 #7000


## Import-Imports data from post process data
data_calib=np.genfromtxt(source_dir+'\\'+file_name_calib+extension,delimiter=',',skip_header=9)

Temp=data_calib[:,4]
ChA=data_calib[:,5]
ChB=data_calib[:,6]
Ref=data_calib[:,7]
RatA=data_calib[:,9]
RatB=data_calib[:,10]

data_target=np.genfromtxt(source_dir+'\\'+file_name_target+extension,delimiter=',',skip_header=9) 

ChA_2=data_target[:,5]
ChB_2=data_target[:,6]
Ref2=data_target[:,7]
Time=np.arange(0,len(ChA_2))
Temp_2=data_target[:,4]

ChA_calib=NDIR_calib('CH4',ChA_2,np.mean(Ref[CH4_times[0]:CH4_times[1]]),Ref2,ChA[zero_voltage_time],CH4,np.mean(ChA[CH4_times[0]:CH4_times[1]]),Temp_2,np.mean(Temp[CH4_times[0]:CH4_times[1]]))
ChB_calib=NDIR_calib('CO2',ChB_2,np.mean(Ref[CO2_times[0]:CO2_times[1]]),Ref2,ChB[zero_voltage_time],CO2,np.mean(ChB[CO2_times[0]:CO2_times[1]]),Temp_2,np.mean(Temp[CO2_times[0]:CO2_times[1]]))   

plt.figure()
plt.plot(ChA,label='ChA')
plt.plot(ChB,label='ChB')
plt.plot(ChA_2,label='CH4')
plt.plot(ChB_2,label='CO2')
plt.ylabel('Voltage, V')
plt.xlabel('Time, s')
plt.legend(loc=0)

plt.figure()
plt.plot(ChA_calib,label='CH4')
plt.plot(ChB_calib,label='CO2')
plt.ylabel('Conc., %')
plt.xlabel('Time, s')
plt.legend(loc=0)


plt.show()

if Save==True:
    save_data=np.vstack([Time,ChA_calib,ChB_calib])
    save_data=np.transpose(save_data)
    np.savetxt(save_dir+'\\'+file_name_save+extension,save_data,delimiter=',',header='Time,CH4,CO2',comments='')