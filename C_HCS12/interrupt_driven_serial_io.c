/*
interrupt driven serial I/O

- Program that uses interrupt driven serial i/o
interrupt is triggered by serial input
program then outputs the received serial input

- Board is running at 24MHz
- Dragon_12: A. Taras, L. Thayalkrishnan, J. Sun, J. Tran
- Last Updated 21/3/2020 Coding Documentation and Explanations
- Functions:
-> Serial_Configuration
-> 21 (serial_interrupt)
*/
#include <hidef.h>
#include "derivative.h"

// buffer for receiving user input
char user_input[500];
// keep track of the individual strings being transmitted
static int string_position;
// keep track of the amount of characters received
int received_count;
// keep track of the amount of characters transmitted
int transmitted_count;

// function declaration
void serial_configuration(void);
interrupt 21 void serial_interrupt(void);

// Main
void main(void){
  // set navigation posotion for string printing
  string_position = -1;
  // configure the serial port
  serial_configuration();

  // configure counters
  received_count = 0;
  transmitted_count = 0;

  // enable interrupts
  EnableInterrupts;
  // wait right here for interrupts
  while(1);
}


// This function configures the inital values for the serial input
void serial_configuration(void){
  const int BAUDRATE = 0x9C;
  const int ENABLE_FLAGS = 0x2C;

  // set baud rate to 9600
  // enable receiver interrupt, receiver and transmitter
  SCI1BDL = BAUDRATE;
  SCI1CR2 = ENABLE_FLAGS;
  return;
}


// This function checks if a character has been inputted, takes the input, and sends back the input with a confirmation message
interrupt 21 void serial_interrupt(void){
  const int BYTE_RECEIVED = 0x20;
  const int TRANSMISSION_READY = 0x80;
  const int ENABLE_TRANSMISSION = 0xAC;
  const int DISABLE_TRANSMISSION = 0x2C;

  // return message
  char string[] = " data recieved\r\n";

  // Receive User input
  // check if a byte has been received
  if(SCI1SR1 & BYTE_RECEIVED){
    // if a byte has been received store it in our buffer
    user_input[received_count] = SCI1DRL;

    // increase the received count
    received_count++;

    // enable transmitter interrup to trigger transmission
    SCI1CR2 = ENABLE_TRANSMISSION;
  }
  // Transmit Input + string
  if(SCI1SR1 & TRANSMISSION_READY){

    // if we have received more than we have sent, loop over this
    // until we transmitted the same amount as we have received
    if(transmitted_count < received_count){

      // if, output the byte received
      // else, output the return message
      if(string_position == -1){
        SCI1DRL = user_input[transmitted_count];
      }
      else if(string_position >= 0){
        SCI1DRL = string[string_position];
      }

      string_position++;
      // check if we are at the end of the string
      if(string_position == 16){
        // reset string_positionition counter
        string_position = -1;
        // increase the transmitted count
        transmitted_count++;
      }
    }
    else{
      // reset the transmitter flag to disable transmission
      // we can go back to receiving now
      SCI1CR2 = DISABLE_TRANSMISSION;
      transmitted_count = 0;
      received_count = 0;
    }
  }
}
