/*
to get pitch

we must loop through some samples of the accelerometer
average them 
apply any offsets 

then 
pitch angle = arctan2(acc_x, acc_z)

convert the angle to degrees 

*/

/*
to get the heading  fromt he magnetometer

heading = atan2(mg_z, mg_y) * 57.2958f;
return heading * 100


*/

/*
converting to cartesian

where a is between the 2d x-y plane
w is the elevation angle 
x = r cos(w) sin (a)
y = r cos(w) cos(a)
x = r sin(w)

*/
#include "iic.h"
#include "magnetometer.h"
#include "accelerometer.h"
#include "gyroscope.h"
#include "sensors.h"
#include "math.h"

MagSensor magnetometer;
AccSensor accelerometer;

//---------------------------------------------------------------------------------
// Magnotomter 
//---------------------------------------------------------------------------------

// Magnetometer initialisation
void magnetometer_init(void){
    int  temp;
    temp=iicstart(magnet_wr);
    temp=iictransmit(HM5883_MODE_REG);
    temp=iictransmit(0x00);
    iicstop();
}

// Magnetormeter acquire
void magnetometer_get(void){
    uint8_t i = 0;
    uint8_t buff[6];
    int temp;
        
    temp=iicstart(magnet_wr);
    temp=iictransmit(HM5883_DATAX0 );
    temp= iicrestart(magnet_rd); 
    iicswrcv();
    
    for(i=0; i<4  ;i++) {
        buff[i]=iicreceive();
    }
    
    buff[i]= iicreceivem1();
    buff[i+1]= iicreceivelast();

    magnetometer.mx = ((buff[0] << 8) | buff[1]);// converts measurement from 2 , store them in struct 
    magnetometer.my = ((buff[2] << 8) | buff[3]);// converts measurement from 2 , store them in struct 
    magnetometer.mz = ((buff[4] << 8) | buff[5]);// converts measurement from 2 , store them in struct 
}

int magnetometer_heading(void){
    volatile float mag_y, mag_z;
    volatile float mag_heading;

    magnetometer_get();
    mag_heading = atan2((float)magnetometer.mz, (float)magnetometer.my);
    return (int)(mag_heading);
}


//---------------------------------------------------------------------------------
// Gyroscope
//---------------------------------------------------------------------------------

// Gyroscope test
// test the precense of Gyro , should get 211 on return
void gyroscope_test(void) {
    int temp,who; 
    
    temp=iicstart(0xD2);
    temp=iictransmit(L3G4200D_WHO_AM_I);
    
    temp=iicrestart(0xD3);
    who=iicreceiveone();
    //who=who & 0x00ff;     Debugging  info
    //PORTB=  who ;
}


//  Gyroscope Initialisation
void gyroscope_init (void) {
    int  temp;

    temp=iicstart(gyro_wr);
    temp=iictransmit(L3G4200D_CTRL_REG1);  // ; 100hz, 12.5Hz, Power up
    temp=iictransmit(0x0f );
    iicstop();  
}


// Gyroscope acquire
void gyroscope_get(int *gxraw, int *gyraw, int *gzraw) {
    uint8_t i = 0;
    uint8_t buff[6];
    int temp;

    temp=iicstart(gyro_wr);
    temp=iictransmit(L3G4200D_OUT_XYZ_CONT);
    temp= iicrestart(gyro_rd); 

    iicswrcv();

    for(i=0; i<4  ;i++) {
        buff[i]=iicreceive();
    }

    buff[i]= iicreceivem1();
    buff[i+1]= iicreceivelast();

    *gxraw = ((buff[1] << 8) | buff[0]);
    *gyraw = ((buff[3] << 8) | buff[2]);
    *gzraw = ((buff[5] << 8) | buff[4]);
}

//---------------------------------------------------------------------------------
// Accelerometer
//---------------------------------------------------------------------------------

// Accelerometer initialisation
void accelerometer_init (void){
    int  temp;
    
    temp=iicstart(accel_wr);
    temp=iictransmit(ADXL345_POWER_CTL);
    temp=iictransmit(0x08 );
    
    temp=iictransmit(ADXL345_DATA_FORMAT);
    temp=iictransmit(0x08 );
    iicstop();
}


// Accelerometer acquire
void accelerometer_get(){
    uint8_t i = 0;
    uint8_t buff[6];
    int temp;
    
    temp=iicstart(accel_wr);
    temp=iictransmit(ADXL345_DATAX0);
    temp= iicrestart(accel_rd); 
    iicswrcv();
    
    for(i=0; i<4  ;i++) {
        buff[i]=iicreceive();
    }
    
    buff[i]= iicreceivem1();
    buff[i+1]= iicreceivelast();

    accelerometer.ax = ((buff[1] << 8) | buff[0]);
    accelerometer.ay = ((buff[3] << 8) | buff[2]);
    accelerometer.az = ((buff[5] << 8) | buff[4]);
}

int accelerometer_pitch(void){
    volatile long int sum_acc_x = 0;
    volatile long int sum_acc_z = 0;
    volatile float acc_x;
    volatile float acc_z;
    volatile float pitch_angle;
    volatile int pitch;
    unsigned char j = 0;

    // loop and get some values for the average 
    for (j = 0; j < 5; j++){
        accelerometer_get();
        sum_acc_x += accelerometer.ax;
        sum_acc_z += accelerometer.az;
    }
    acc_x = (float)(sum_acc_x/5);
    acc_z = (float)(sum_acc_z/5);
    pitch_angle = atan2(acc_x, acc_z);
    pitch = (int)(pitch_angle * 57.29);
    return pitch
}