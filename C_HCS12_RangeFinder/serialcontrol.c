#include <hidef.h>
#include "derivative.h"
#include <stdio.h>
#include "iic.h"
#include "pll.h"
#include "sci1.h"
//#include "lcd.h"
// #include "keypad.h"
//#include "sevenseg.h"
#include "scan.h"
#include "lidar.h"
#include "sensors.h"
#include "scan.h"
#include "serialcontrol.h"

/*
/// This function is used to manually move the PTU
///
/// Uses the baord to manually move the PTu up, down left and right
/// @see pwm_delay()
void custom_scan(void){
// configure pwm bounds
  int count;
  count = 0;
  i = 2700;
  j = max_j; //adjusted for maximum elevation

  direction = 1; // go right initially
  // goes up and down
  PWMDTY5 = (j & 0xFF);     // low bits
  PWMDTY4 = (j >> 8);       // high bits
  // goes left to right
  PWMDTY7 = (i & 0xFF);     // low bits
  PWMDTY6 = (i >> 8);       // high bits

  while(1) {

    pwm_delay();
    if (j>=min_j)
    //adjusted for minimum elevation
    {
      // move right across
      if (direction==1){
        if (i < pwm_max){   //adjusted for max azimuth
          i+=step_size;
          PWMDTY7 = (i & 0xFF);
          PWMDTY6 = (i >> 8);
        }else{
          i == pwm_max;
          direction = 0;
          j-=step_size;
          PWMDTY5 = (j & 0xFF);
          PWMDTY4 = (j >> 8);

        }
      }
      // move left across
      if (direction==0){
        if (i > pwm_min){    //adjusted for min azmimuth
          i-=step_size;
          PWMDTY7 = (i & 0xFF);
          PWMDTY6 = (i >> 8);
        }
        else{
          i == pwm_min;
          direction = 1;
          j-=step_size;
          PWMDTY5 = (j & 0xFF);
          PWMDTY4 = (j >> 8);
        }
      }

    }
  }
}

*/

/// This function configures the user input using serial communication
///
/// First, the user inputs the command with a terminating character. Program then processes the input saved in the buffer
/// @see SCI1_InString() SCI1_OutString() SCI1_InChar()
void input_configuration(void){

  int no = 0;

  SCI1_InString(buffer, BUFFER_SIZE);
  SCI1_OutString("\r\n");
  // SCI1_OutString("buffer = ");
  // SCI1_OutString(buffer);
  // SCI1_OutString("\r\n");

  check_confirm();
  // Check if the user inputted a carriage return
  if (newline == 1){
    // Disable receiver
    SCI1CR2 = DISABLE_RECEIVER;
    SCI1_OutString("Processing Input...\r\n");

    // Function for Live Quick
    if (buffer[1] == 'l' && buffer[3] == 'q'){
      SCI1_OutString("Setting: Live Quick Scan\r\n");
      configuration.is_quickscan = 1;

    // Function for Live Deep
    } else if (buffer[1] == 'l' && buffer[3] == 'd'){
      SCI1_OutString("Setting: Live Deep Scan\r\n");
      configuration.is_deepscan = 1;

    // Function for Live Custom
  } else if (buffer[1] == 'l' && buffer[3] == 'c'){
      SCI1_OutString("Setting: Live Custom Scan\r\n");
      configuration.is_customscan = 1;
      for (string_position = 5; string_position < BUFFER_SIZE; string_position++){
        // SCI1_OutString("This is going in the loop -->");
        // SCI1_OutChar(buffer[i]);
        // SCI1_OutString("\r\n");
        configure_custom(buffer[string_position], string_position);
      }


    // Function for Offline Quick
    } else if (buffer[1] == 'o' && buffer[3] == 'q'){
      SCI1_OutString("Setting: Offline Deep Scan\r\n");
      configuration.is_offline_quickscan = 1;

    // Function for Offline Deep
    } else if (buffer[1] == 'o' && buffer[3] == 'd'){
      SCI1_OutString("Setting: Offline Quick Scan\r\n");
      configuration.is_offline_deepscan = 1;

    // Function for Offline Custom
    } else if (buffer[1] == 'o' && buffer[3] == 'c'){
      SCI1_OutString("Setting: Offline Custom Scan\r\n");
      configuration.is_offline_customscan = 1;
      for (string_position = 5; string_position < BUFFER_SIZE; string_position++){
        configure_custom(buffer[string_position], string_position);
      }

    // Function for testing
    } else if (buffer[1] == 't'){
      SCI1_OutString("Testing...\r\n");
      configuration.

      //custom_scan();

    // Function for calibration
    } else if (buffer[1] == 'c'){
      SCI1_OutString("Calibrating...\r\n");
      
    // Function for help
    } else if (buffer[1] == 'h'){
      SCI1_OutString("Refer to diagram: Example:\r\n-l-q. [live quick]\r\n-l-c-a=000,111. [live custom, azimuth (0-111)]\r\n");

    } else {
      SCI1_OutString("There is an error in the input command. Please try again\r\n");
      no = 1;
    }

    // Empty out the entire buffer
    for (string_position = 0; string_position < BUFFER_SIZE; string_position++){
      buffer[string_position] = '\0';
    }

    newline = 0;

    if (no == 0){

      get_distance();

    }


    SCI1CR2 = ENABLE_RECEIVER;
  }

}

/// This function chooses the correct custom setting to change
///
/// Settings are based on the user input. Must ensure all bounds follow the correct syntax
/// @param type THis is the custom setting (etc. 'a','e','n'....)
/// @param position This is the position of the custom setting inthe buffer
/// @return Returns nothing
/// @see capture_bounds(int j)
void configure_custom(char type, int position){
    if (type == 'a'){
      SCI1_OutString("Customizing Azimuth...\r\n");
      SCI1_OutString("Lower Bound = ");
      configuration.azimuth_min = capture_bounds(position);
      SCI1_OutString("Upper Bound = ");
      configuration.azimuth_max = capture_bounds(position + 4);

    } else if (type == 'e'){
      SCI1_OutString("Customizing Elevation...\r\n");
      SCI1_OutString("Lower Bound = ");
      configuration.elevation_min = capture_bounds(position);
      SCI1_OutString("Upper Bound = ");
      configuration.elevation_max = capture_bounds(position + 4);

    } else if (type == 's'){
      SCI1_OutString("Customizing Steps...\r\n");
      SCI1_OutString("Angle = ");
      configuration.step_size = capture_bounds(position);

    } else if (type == 'n'){
      SCI1_OutString("Customizing Samples...\r\n");
      SCI1_OutString("Samples = ");
      configuration.samples_per_orientation = capture_bounds(position);

    } else if (type == 'f'){
      SCI1_OutString("Customizing Frequency...\r\n");
      SCI1_OutString("Frequency = ");
      configuration.scan_frequency = capture_bounds(position);
    }
}

/// This function captures the user's inputted bound
///
/// This function simply converts the 2nd,3rd,4th next position in the buffer and converts to decimal
/// @param j  This is the position of the custom setting (et. 'a' or 'e'...)
/// @return Returns a number in decimal format
short int capture_bounds(int j){
  int bound;
  int k;
  int error = 0;

  // Error Checking
  if (buffer[j+2] == '-' && ascii_to_decimal(buffer[j+3]) > 6){
    error = 1;
  }

  if (ascii_to_decimal(buffer[j+2]) > 1 ){
    error = 2;
  }

  if (buffer[j+4] < 48 || buffer[j+4] > 57){
    error = 3;
  }

  if (error == 0){
    if (buffer[j+2] == '-'){
      bound = -1*ascii_to_decimal(buffer[j+3])*10 + ascii_to_decimal(buffer[j+4]);
      // This is to print out the bounds
        for (k = 2; k < 5; k++){
          SCI1_OutChar(buffer[j+k]);
        }
        SCI1_OutString("\r\n");
    } else {
      bound = ascii_to_decimal(buffer[j+2])*100 + ascii_to_decimal(buffer[j+3])*10 + ascii_to_decimal(buffer[j+4]);
      // This is to print out the bounds
        for (k = 2; k < 5; k++){
          SCI1_OutChar(buffer[j+k]);
        }
        SCI1_OutString("\r\n");
    }
  } else {
    SCI1_OutString("Error ");
    SCI1_OutChar(error + '0');
    SCI1_OutString(". Invalid input for above customisation. Resetting to default\r\n");
  }

  return bound;
}

/// THis function converts an ascii input to decimal
///
/// This function converts the character into decimal, then subtracts 48 ('0') in order to get the correct integer
/// @param character THis is the character to be converted
short int ascii_to_decimal(char character){
  return character - '0';
}

/// This function checks if the buffer contains the terminating character
///
/// The user must input the termininating character for the input to be analysed. In this case it is a full stop ('.')
void check_confirm(void){
  for (string_position = 0; string_position < BUFFER_SIZE; string_position++){
    if ((buffer[string_position] == '.')){
      newline = 1;
    }
  }
}
