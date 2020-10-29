/*
Program that reads the voltage on pin pad7
  pin pad7 controls voltage , from 0 to 5V
it then displays the voltage on the 7 segment displays
  correct to one significant figure

1) configure analog to digital converter
2) configure leds
3) read from pin pad 7
4) the value we extract will be a voltage reading from 0-5v, we want 
   to display this value correct to 2 sig figs, so we need to represent 
   the values from 0.0 to 5.0, so 50 values. 
4) convert the output by dividing it by 50. As it doesnt divide evenly
   we will apply boundary conditions to force the displayed value to 50 
   if its above a threshold
5) push that value to be display to the seven seg
6) loopity loop
*/

// imports 
#include <hidef.h>
#include "derivative.h"
#include "tron.h"

// function declaration
void voltage_to_digital(unsigned int ADC_OUTPUT); 
void seven_seg_configuration(void);
void adc_configuration(void);
void delay(void);


// Main Function 
void main(void){
  const int NEW_CONVERSION = 0x87;
  const int CONVERSION_READY = 0x80;
  
  // configure board 
  seven_seg_configuration();
  adc_configuration();

  // loop by first triggereing a new conversion
  // then waiting for the conversion flag to be set
  // when it is set, send the value to be converted and puhsed to port B 
  while (1){
    ATD0CTL5 = NEW_CONVERSION;

    while(!(ATD0STAT0&CONVERSION_READY));

    voltage_to_digital(ATD0DR0L);
  }
}


#include <hidef.h>
#include "derivative.h"


// first configure the ADC
// ATD0CTL2 controls the mode of the ADC - set the MSB high to enable ADC
// ATD0CTL3 controls the conversion sequence lenght - set to 08 [0000 1000] for one conversion per sequence
// ATD0CTL4 controls the frequency, rsolution and the sample time - set to EB - 8 bit resolution, 16 conversion periods, prescaler value
// ATD0CTL5 controls the conversion sequence type
// ATDSTAT0 status register - set to 80 [1000 0000], sequence complete flag
// ATD0DR0L reulst register - grab the result from here
void adc_configuration(void){
  const int CONVERSION_ON = 0x80;
  const int CONVERSION_LENGTH = 0x08;
  const int CONVERSION_FORMAT = 0xEB;
  
  ATD0CTL2 = CONVERSION_ON;
  ATD0CTL3 = CONVERSION_LENGTH;
  ATD0CTL4 = CONVERSION_FORMAT;
}

// Configure the LEDs

void seven_seg_configuration(void){
  const int SETHIGH = 0xFF;
  const int SETLOW = 0x00;
  DDRB = SETHIGH;
  DDRP = SETHIGH;
  DDRJ = SETHIGH;
  PTJ = SETLOW;
}

// delay
void delay(void){
  unsigned short count = 1000;
  while(count > 0){
    count -=1;
  }
}

// variables 
void voltage_to_digital(unsigned int ADC_OUTPUT){
  const int FIRST_DISPLAY = 0x0E;
  const int SECOND_DISPLAY = 0x0D;
  const int DECIMAL_POINT = 0x80;

  int ONES;
  int POINT_ONES;
  unsigned int SEVEN_SEG_NUMS[10] = {63, 6, 91, 79, 102, 109, 125, 7, 127, 111};
  
  // if the number here is greater than 50 we force it to 50
  ADC_OUTPUT /= 5;
  if(ADC_OUTPUT>=50) ADC_OUTPUT = 50;

  // using regular division and modulo division we can extract 
  // the ones value and then the point ones 
  ONES = SEVEN_SEG_NUMS[ADC_OUTPUT/10] + DECIMAL_POINT;
  POINT_ONES = SEVEN_SEG_NUMS[ADC_OUTPUT%10];

  
  PTP = FIRST_DISPLAY;
  PORTB = ONES;
  delay();
  PTP = SECOND_DISPLAY;
  PORTB = POINT_ONES;
  delay();
}