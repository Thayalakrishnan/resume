#ifndef lidar_H
#define lidar_H

#define MAX_TIMER_COUNT = 65536;
#define COUNTS_PER_MS = 24;

void get_distance(void);
void pulse_width_measure(void);
void init_lidar(void);

#endif