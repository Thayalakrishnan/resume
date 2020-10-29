#include <hidef.h>
#include "derivative.h"
#include <math.h>
#include <float.h>
#include "iic.h"
#include "pll.h"
#include "sci1.h"
#include "scan.h"
#include "lidar.h"
#include "sensors.h"
#include "scan.h"
#include "serialcontrol.h"


// initialise pwm
void pwm_init(void){
    PWMCTL = 0xC0; // 1100 0000
    PWMCLK = 0xA0; // 1010 0000
    PWMPOL = 0xA0; // 1010 0000
    PWMPRCLK = 0x22; //0010 0010
    PWMSCLA = 0x01; //0000 0001
    PWMPER4 = 0xEA; //
    PWMPER5 = 0x60; //
    PWMSCLB = 0x01; //0000 0001
    PWMPER6 = 0xEA; //
    PWMPER7 = 0x60; //
    PWME = 0xF0; // 1111 0000
}

/// This function automatically moves the PTU unit
void ptu_move(void){
  DisableInterrupts;
  if (ptu.current_elevation >= configuration.elevation_min){
    // move right across
    if (ptu.current_direction == 1){
      if (ptu.current_azimuth < configuration.azimuth_max){
        ptu.current_azimuth += configuration.step_size;
        PWMDTY7 = (ptu.current_azimuth & 0xFF);
        PWMDTY6 = (ptu.current_azimuth >> 8);
      }else {
        ptu.current_azimuth == configuration.azimuth_max;
        ptu.current_azimuth = 0;
        ptu.current_elevation -= configuration.step_size;
        PWMDTY5 = (ptu.current_elevation & 0xFF);
        PWMDTY4 = (ptu.current_elevation >> 8);
      }
    }
    // move left across
    if (ptu.current_direction == 0){
      if (ptu.current_azimuth > configuration.azimuth_min){
        ptu.current_azimuth -= configuration.step_size;
        PWMDTY7 = (ptu.current_azimuth & 0xFF);
        PWMDTY6 = (ptu.current_azimuth >> 8);
      }else {
        ptu.current_azimuth == configuration.azimuth_min;
        ptu.current_azimuth = 1;
        ptu.current_elevation -=configuration.step_size;
        PWMDTY5 = (ptu.current_elevation & 0xFF);
        PWMDTY4 = (ptu.current_elevation >> 8);
      }
    }
  EnableInterrupts;
  }
}

