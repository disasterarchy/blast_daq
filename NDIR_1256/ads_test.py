ADC = ADS1256.ADS1256()
ADC.ADS1256_init()
y = 0
x= 0
start = datetime.now()
arr = np.
while y<nn:
    try:
        dt = datetime.now() - start
        arr[x] = [dt.total_seconds(),
                  ADC.ADS1256_GetChannalValue(0)*5.0/0x7fffff,
                  ADC.ADS1256_GetChannalValue(1)*5.0/0x7fffff,
                  ADC.ADS1256_GetChannalValue(2)*5.0/0x7fffff,
                  22]  #TODO replace with Temperature measurement
