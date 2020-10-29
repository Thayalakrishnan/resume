#include <hidef.h>
#include "derivative.h"
#include <math.h>
#include <float.h>
#include <stdio.h>
#include "iic.h"
#include "pll.h"
#include "sci1.h"
// #include "keypad.h"
#include "scan.h"
#include "lidar.h"
#include "sensors.h"
#include "scan.h"
#include "serialcontrol.h"

void get_distance(void){
  int distance_array[3];
  float flt_deviation,flt_average,lower_bound,upper_bound;
  float flt_sum_distance, flt_variance=flt_sum_distance=0.0;
  int index_i,index_j,k;

  for(index_i = 0; index_i < 3; index_i++){
      pulse_width_measure();
      distance_array[index_i] = distance;
      flt_sum_distance += distance;
  }

  flt_average = flt_sum_distance/index_i;                            // calculate the average
  for (index_j = 0; index_j < 3; ++index_j){
    flt_variance += pow(distance_array[index_j] - flt_average, 2);   // calculate the variance
  }

  flt_deviation = sqrt(flt_variance/3);                        // calcualte the standard deviation
  flt_sum_distance = 0.0;
  index_i = 0;
  lower_bound = flt_average - 2*flt_deviation;                 // set acceptable bounds
  upper_bound = flt_average + 2*flt_deviation;                 // set acceptable bounds

  for (k = 0; k < 3; ++k){                                      // filter out the shit data
    if (distance_array[k] > lower_bound || distance_array[k] < upper_bound){
      flt_sum_distance+= distance_array[k];
      index_i++;
    }
  }
  flt_average = flt_sum_distance/i;

  // convert to printable format
  
  standard_deviation = floor((unsigned short) flt_deviation);

  if (standard_deviation < 200){
      sample.measured_distance = floor((unsigned short) flt_average);
  }
}


void pulse_width_measure(void){
  overflow_counter = 0;
  DisableInterrupts;
  TSCR1 |= 0x90;           // enable timer and fast flag clear
  TSCR2 |= 0x00;           // prescale by none
  TIOS &=  ~0x02;          // select input capture 1, set low
  TCTL4 |= 0x04;           // prepare to capture the rising edge risingA
  TFLG1 |= 0x02;           // clear the C1F Flag
  TFLG2 |= 0x80;           // clear TOF flag
  PTH &= ~0x01;            // trigger the lidar
  while(!(TFLG1 & 0x02));  // wait for the arrival of the rising edge
  TSCR2 |= 0x80;           // enable TCNT overflow interrupt
  TFLG1 |= 0x02;           // clear the C1F Flag
  EnableInterrupts;        // Enable interrupts briefly
  TCTL4 |= 0x08;           // prepare to capture the falling edge risingB
  rising = TC1;            // read the edge count
  while(!(TFLG1 & 0x02));  // wait for the arrival of the falling edge
  DisableInterrupts;       // Disable interrupts briefly
  TSCR2 &= ~0x90;
  TSCR1 &= ~0x80;
  distance = ((MAX_TIMER_COUNT - rising) + TC1 + overflow_counter*MAX_TIMER_COUNT)/COUNTS_PER_MS;
  EnableInterrupts;
  // distance = distance*CALIBRATION_COEFF;  // i havent set this yet, but i intend to use it
}


/// This function initialises the LIDARt
void init_lidar(void){
    PTH |= 0x01;   // we set this high when we dont want the lidar to take readings
    DDRH |= 0x01;  // set pin 0 of port H for trigger output
}
