#ifndef scan_H
#define scan_H

// custom scan config
typedef struct {

    unsigned short azimuth_min;
    unsigned short azimuth_max;
    unsigned short elevation_min;
    unsigned short elevation_max;
    unsigned short step_size;
    unsigned short scan_frequency;
    unsigned char samples_per_orientation;

    unsigned char is_quickscan;
    unsigned char is_customscan;
    unsigned char is_deepscan;
    unsigned char is_offline_quickscan;
    unsigned char is_offline_customscan;
    unsigned char is_offline_deepscan;
    unsigned char currently_scanning;

} ScanConfig;

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