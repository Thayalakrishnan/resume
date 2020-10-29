#ifndef READINGS_H
#define READINGS_H

typedef struct {

    unsigned short current_azimuth;
    unsigned short current_elevation;
    char current_direction;

} PanandTilt;

typedef struct {

    unsigned short current_azimuth;
    unsigned short current_elevation;
    unsigned short measured_distance;
    unsigned short measured_heading_radians;
    unsigned short measured_heading;
    unsigned short measured_pitch_radians;
    unsigned short measured_pitch;
    unsigned short measured_x;
    unsigned short measured_y;
    unsigned short measured_z;
    
} ScanValues;

#endif