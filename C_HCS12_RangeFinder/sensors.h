#ifndef sensors_H
#define sensors_H

// Accelerometer    accelerometer   ACCELEROMETER
#define accel_wr                0xA6
#define accel_rd                0xA7
#define ADXL345_POWER_CTL       0x2D
#define ADXL345_DATAX0          0x32
#define ADXL345_DATA_FORMAT     0x31


// Magnetometer     magnetometer    MAGNETOMETER
#define magnet_wr               0x3C
#define magnet_rd               0x3D
#define HM5883_MODE_REG         0x02
#define HM5883_DATAX0           0x03


// Gyroscope    gyroscope           GYROSCOPE
#define gyro_wr                 0xD2
#define gyro_rd                 0xD3
#define L3G4200D_WHO_AM_I       0x0F
#define L3G4200D_CTRL_REG1      0x20
#define L3G4200D_OUT_XYZ_CONT   0xA8

#endif