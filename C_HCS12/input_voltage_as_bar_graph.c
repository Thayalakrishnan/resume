/*
Program that reads the voltage on pin pad7
  pin pad7 controls voltage , from 0 to 5V
it then displays the voltage on the 8 LEDs
  display the result as a bar graph

1) configure analog to digital converter
2) configure leds
3) read from pin pad 7
4) convert into led value by dividing by 8 (8 LEDs)
      so each LED represents 31 
5) push that value to be display on the LEDs
6) loopity loop
*/

// imports 
#include <hidef.h>
#include "derivative.h"

// set constants
const int LED_INTERVAL = 31;
const int HIGH = 0xFF;
const int LOW = 0xFF;     
const int CONVERSION_ON = 0x80;
const int CONVERSION_LENGTH = 0x08;
const int CONVERSION_FORMAT = 0xEB;
const int NEW_CONVERSION = 0x87;
const int NEW_CONVERSION_FLAG = 0x80;


// declare functions
void led_configuration(void);
void adc_configuration(void);

// variables 
unsigned int voltage_to_bar(unsigned int ADC_OUTPUT){
  int LED_BAR_REPR = ADC_OUTPUT/LED_INTERVAL;

  // if the value is 8, turn on all LEDs
  // if the value is 0, turn off all LEDs
  // Else, bit shift the value to the correct number from 1-7
  if (LED_BAR_REPR==8){
    return (0xFF);
  }
  else if (LED_BAR_REPR==0){
    return (0x00);
  }
  else{
    return (0xFF>>(8-LED_BAR_REPR));
  }
}

// Main Function 
void main(void){
  // configure board 
  led_configuration();
  adc_configuration();

  // loop by first triggereing a new conversion
  // then waiting for the conversion flag to be set
  // when it is set, send the value to be converted and puhsed to port B 
  while (1){
    ATD0CTL5 = NEW_CONVERSION;
    while(!(ATD0STAT0&NEW_CONVERSION_FLAG));
      PORTB = voltage_to_bar(ATD0DR0L);
  }
}

// first configure the ADC
// ATD0CTL2 controls the mode of the ADC - set the MSB high to enable ADC
// ATD0CTL3 controls the conversion sequence lenght - set to 08 [0000 1000] for one conversion per sequence
// ATD0CTL4 controls the frequency, rsolution and the sample time - set to EB - 8 bit resolution, 16 conversion periods, prescaler value
// ATD0CTL5 controls the conversion sequence type
// ATDSTAT0 status register - set to 80 [1000 0000], sequence complete flag
// ATD0DR0L reulst register - grab the result from here 
void adc_configuration(void){
  ATD0CTL2 = CONVERSION_ON;
  ATD0CTL3 = CONVERSION_LENGTH;
  ATD0CTL4 = CONVERSION_FORMAT;
}
// Configure the LEDs
void led_configuration(void){
  DDRB = HIGH;
  DDRJ = HIGH;
  PTJ = LOW;
}