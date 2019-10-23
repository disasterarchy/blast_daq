
originalcode = open('ADS1256.template','r').read()

import os

def make():
    stream = os.popen('make')
    output = stream.read()
    return output

def execute():
    stream = os.popen('sudo ./ads1256_test')
    output = stream.read()
    return output
arr = []
for sample_rate in ['ADS1256_30000SPS', 'ADS1256_15000SPS', 'ADS1256_7500SPS', 'ADS1256_3750SPS','ADS1256_2000SPS']:
    newcode = originalcode.replace('ADS1256_30000SPS',sample_rate)
    for delay_ReadData2 in [250,500,750,1000,1250]:
        newcode = newcode.replace('1002',str(delay_ReadData2))
        for delay_ReadData3 in [250,500,750,1000,1250]:
            newcode = newcode.replace('1003',str(delay_ReadData3))
            for delay_ReadData4 in [250,500,750,1000,1250]:
                newcode = newcode.replace('1004',str(delay_ReadData3))
                f = open('obj/ADS1256.c','w')
                f.write(newcode)
                f.close()
                make()
                for x in range(1,5):
                    output= execute()
                    arr.append([output[-5:], sample_rate, delay_ReadData2, delay_ReadData3, delay_ReadData4])
                    print(output, sample_rate, delay_ReadData2, delay_ReadData3, delay_ReadData4)
                

    



