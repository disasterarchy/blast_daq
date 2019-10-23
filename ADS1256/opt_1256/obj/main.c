#include <stdlib.h>     //exit()
#include <signal.h>     //signal()
#include <time.h>
#include "ADS1256.h"
#include "stdio.h"
#include <time.h>
#include <string.h>
#include <sys/timeb.h>

//#define <sched.h>
//#define <sys/mman.h>


void  Handler(int signo)
{
    //System Exit
    printf("\r\nEND                  \r\n");
    DEV_ModuleExit();

    exit(0);
}

int main(void)
{
    UDOUBLE ADC[8],i;
    struct timeb start, end;
    int diff;
    int x =0;
    int X =0;
    float XX[8][1000];
    float tt[1000];
    
    //Code snippet to make faster (doesn't work)
    //struct sched_param sp;
    //memset(&sp, 0, sizeof(sp));
    //sp.sched_priority = sched_get_priority_max(SCHED_FIFO);
    //sched_setscheduler(0, SCHED_FIFO, &sp);
    //mlockall(MCL_CURRENT | MCL_FUTURE);
    
    printf("demo\r\n");
    DEV_ModuleInit();
    
    // Exception handling:ctrl + c
    signal(SIGINT, Handler);

    if(ADS1256_init() == 1){
        printf("err");
        DEV_ModuleExit();
        exit(0);
    }
    
    FILE *fp;
    fp = fopen("/tmp/test.csv", "w+");
    fprintf(fp, "1 \n");   
    ftime(&start);
    
    
    
    
    
    
    while( diff<1000 ){
    

        
        // printf("0 : %f\r\n",ADS1256_GetChannalValue(0)*5.0/0x7fffff);
        // printf("1 : %f\r\n",ADS1256_GetChannalValue(1)*5.0/0x7fffff);
        // printf("2 : %f\r\n",ADS1256_GetChannalValue(2)*5.0/0x7fffff);
        // printf("3 : %f\r\n",ADS1256_GetChannalValue(3)*5.0/0x7fffff);
        // printf("4 : %f\r\n",ADS1256_GetChannalValue(4)*5.0/0x7fffff);
        // printf("5 : %f\r\n",ADS1256_GetChannalValue(5)*5.0/0x7fffff);
        // printf("6 : %f\r\n",ADS1256_GetChannalValue(6)*5.0/0x7fffff);
        // printf("7 : %f\r\n",ADS1256_GetChannalValue(7)*5.0/0x7fffff);
        
        ADS1256_GetAll(ADC);
               
        for(i=0;i<8;i++){
            //printf("%d %f\r\n",i,ADC[i]*5.0/0x7fffff);
            XX[i][x] = ADC[i]*5.0/0x7fffff;
            ftime(&end);
            tt[x] = end.time + end.millitm;
            //XX[i][x] = 2.4563*5.0/0x7fffff;

        }
        //printf("\33[8A");//Move the cursor up 8 lines
    x++;
    diff = (int) (1000.0* (end.time - start.time) + (end.millitm - start.millitm));
    }
    ftime(&end);
    diff = (int) (1000.0* (end.time - start.time) + (end.millitm - start.millitm));
    
    for (X=0;X<1000;X++){
        fprintf(fp, " %d,  %f", X, tt[X]);
        for(i=0;i<8;i++){
            fprintf(fp, ", %f ", XX[i][X]);
        }
        fprintf(fp, " \r\n");
    }
    
    fclose(fp);
    printf("Done %u-000000000000%d", diff,x);
    return 0;
}
