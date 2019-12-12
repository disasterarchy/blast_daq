import numpy as np
import pickle
from datetime import datetime
## NDIR_Realtime Conversion
## Erik Archibald 10/31/2019 based on NDIR Parser Robert Kennedy 7/22/2019 
zCal = {}
sCal = {}
try:
    zCal['CO2'] = pickle.load(open('ZeroCO2.p','rb'))
    sCal['CO2'] = pickle.load(open('SpanCO2.p','rb'))
    print('Using CO2 calibration from: ' + sCal['CO2']['User'] + sCal['CO2']['Date'].isoformat()[:-7] + " at " +  str(sCal['CO2']['C']) + " % CO2")
except:
    print('CO2 calibrations not found! Using made up values')
    sCal = {'CO2':{'Zero':1.0, 'Span':0.5, 'C':100, 'Tcal':298, 'User':0, 'Board':0, 'Sensor':0, 'Notes':0}}
    zCal['CO2'] = sCal['CO2']
try:
    zCal['CH4'] = pickle.load(open('ZeroCH4.p','rb'))
    sCal['CH4'] = pickle.load(open('SpanCH4.p','rb'))
    print('Using CH4 calibration from: ' + sCal['CH4']['User'] + sCal['CH4']['Date'].isoformat()[:-7] + " at " +  str(sCal['CH4']['C']) + " % CH4")
except:
    print('CH4 calibrations not found! Using made up values')
    sCal['CH4'] = {'Zero':1.0, 'Span':0.5, 'C':100, 'Tcal':298, 'User':0, 'Board':0, 'Sensor':0, 'Notes':0}
    zCal['CH4'] = sCal['CH4']

def CalibrateZero(dv, gas, User='Unspecified', Board='Unspecified', Sensor='Unspecified', Notes='None'):
    Act1 = dv['PkPk1']
    Act2 = dv['PkPk2']
    Ref  = dv['PkPkRef']
    if gas == 'CO2': Act =Act1
    elif gas == 'CH4': Act = Act2
    Zeros = Act / Ref
    Zero = np.median(Zeros)
    ZeroCal = {}
    ZeroCal['Zero'] = Zero
    ZeroCal['User'] = User
    ZeroCal['Board'] = Board
    ZeroCal['Sensor'] = Sensor
    ZeroCal['Notes'] = Notes
    ZeroCal['Date'] = datetime.now()
    ZeroCal['Tcal'] = np.median(dv['Temperature']) + 273.15
    
    pickle.dump(ZeroCal, open('Zero' + gas + '.p', "wb"))
    pickle.dump(ZeroCal, open('Zero' + gas + datetime.now().isoformat()[:-7] + '.p', "wb"))
    zCal[gas] = ZeroCal
    
    
def CalibrateSpan(dv, gas, C, User='Unspecified', Board='Unspecified', Sensor='Unspecified', Notes='None'):
    Act1 = dv['PkPk1']
    Act2 = dv['PkPk2']
    Ref  = dv['PkPkRef']
    if gas=='CO2':
        a=0.106
        n=0.542
        alpha=0.000586
        beta=-0.088
        Act=Act1
    elif gas=='CH4':
        a=0.015
        n=0.464
        alpha=0.000438
        beta=-1.636
        Act=Act2
    Zero=zCal[gas]['Zero']   
    Spans = (1 - (Act)/(Zero*Ref)) / (1-np.math.exp(-a*C**n))
    Span = np.median(Spans)
    SpanCal = {}
    SpanCal['Zero'] = zCal[gas]['Zero']
    SpanCal['Span'] = Span
    SpanCal['User'] = User
    SpanCal['Board'] = Board
    SpanCal['Sensor'] = Sensor
    SpanCal['Notes'] = Notes
    SpanCal['Tcal'] = np.median(dv['Temperature']) +273.15
    SpanCal['Tcal_zero'] = zCal[gas]['Tcal']
    SpanCal['Date'] = datetime.now()
    SpanCal['C'] = C
    pickle.dump(SpanCal, open('Span' + gas + '.p', "wb"))
    pickle.dump(SpanCal, open('Span' + gas + datetime.now().isoformat()[:-7] + '.p', "wb"))
    sCal[gas] = SpanCal
    

def NDIR(gas,PkPk,PkPkRef,Temperature): ## NDIR Concentration Calculation
    #print(gas, PkPk, PkPkRef)
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
        T = Temperature + 273.15
        Zero=sCal[gas]['Zero']
        Span=sCal[gas]['Span']                                #Span
        Tcal = sCal[gas]['Tcal']                              #Temperature
        ratioC=PkPk/(Zero*PkPkRef)*(1+alpha*(T-Tcal))    # Compensated Normalized Ratio
        SpanC=Span+(beta*(T-Tcal)/Tcal)                  #Compensated Span
        if (1-ratioC) > 0.0:
            Conc = max((-np.log(1-((1-ratioC)/SpanC))/a)**(1/n),0)   #Concentration
        else:
            Conc = 0
        return Conc
