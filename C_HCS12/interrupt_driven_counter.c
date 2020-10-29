/*
interrupt driven serial I/O counter

- Program that takes a serial inputs ('d', 'h' or '0-9') and counts from (0-9990)
  decimal or (0-FFFF) hexadecimal with intervals based on the digit entered.

- Board is running at 24MHz
- Dragon_12: A. Taras, L. Thayalkrishnan, J. Sun, J. Tran
- Last Updated 21/3/2020 Coding Documentation and Explanations
- Functions:
-> sciIsr (interrupt)
-> timerIsr (interrupt)
-> displaySeg
-> delay
-> decimal_to_seg
*/

#include <hidef.h>      /* common defines and macros */
#include "derivative.h"      /* derivative-specific definitions */

#include "main_asm.h" /* interface to the assembly module */
#include "mc9s12dg256.h" // has #defines of interrupts

#include <stdlib.h>

#define DEC 'd'
#define HEX 'h'

/* Global Variables: For Small Memory Model */
//	These variables can be seen in a .asm function
unsigned char countMode = 'h';
unsigned int count = 0xF03C;
unsigned int speed = 1;

// Enable lines for each 7 segment
const int SEG_MASK[5] = {0x07,0x0B,0x0D,0x0E,0x00};

// Digits 0 - F in hexadecimal for the 7segment display
const int NUM_TO_SEG[17] = {0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x67,0x77,0x7C,0x58,0x5E,0x79,0x71,0x00};


// Function declerations
interrupt VectorNumber_Vsci1 void sciIsr(void);
interrupt VectorNumber_Vtimch4 void timerIsr(void);
void displaySeg(unsigned int count, unsigned char flag);
void delay(void);
void decimal_to_seg(unsigned int var);



//**************************   MAIN    **********************************//
void main(void) {
  int temp;

  // Configure the Board
  // SCI
  SCI1BDH = 0x00;  // we would set these for higher BRs
	SCI1BDL = 0x9C;  // set baud rate to 9600
	SCI1CR1 = 0x00;  // set 8 data bits, no parity
	SCI1CR2 = 0x24;  // set 2nd bit high, enabling the receiver

  // Timer 4
	TIE = 0x10;      // enable timer interrupt 4
  TCTL1 = 0x01;  	 // set output to toggle
	TIOS = 0x10;     // select channel 4 for output compare
	TSCR1 = 0x90;    // enable timers
	TSCR2 = 0x07;    // prescalar div 128

	// 7 Segs
	DDRB = 0xFF;  // Output
	DDRP = 0xFF;  // Output
	PTP = 0x00;   // Setting cathodes to 0

	EnableInterrupts;

	// reset flag
	temp = SCI1SR1;

  for(;;) {  /* loop forever */
    // always be displaying the count
    displaySeg(count, countMode);
  }
}


//**************************   OTHER FNs    **********************************//

// This function is a serial input routine which changes the display to hexadeximal or decimal (based on user input)
interrupt VectorNumber_Vsci1 void sciIsr(void) {
	unsigned char in = SCI1DRL;
	// reset flag
	int temp = SCI1SR1;

  // check if user inputted a digit
	if('0' <= in && in <= '9'){
	  // user wants to change speed
	  speed = in - '0' + 1;

  // check if user inputted a character
	} else if (in == HEX || in == DEC){

    // convert display to subsequent character
	  countMode = in;

    // If hexadecimal displays a numbr greater 9999, and the user presses 'd', reset counter
	  if (count > 9999 && countMode == DEC){
	    count = 0;
	  }
	} // all bad inputs ignored
	// rti is included automatically
}

// This function is a timer interrupt, that tells the counter to increment everytime TC4 = TCNT and then reloads TC4 with the next period
// It also resets the counter when the count has maxed out
interrupt VectorNumber_Vtimch4 void timerIsr(void) {

  // Check if counter has reached max (9999)
  if (count == 9999 && countMode == DEC){

    // reset counter
	  count = 0;

    // Check if counter has reached max (FFFF)
	} else if (count == 0xFFFF && countMode == HEX){

    // Reset counter
	  count = 0;
	} else {

    // Increment counter 
	  count++;
	}

  // set next interrupt
  TC4 = TCNT + speed*1000+1000;
}


// This function determines which 7segment to turn on and what to display on that corresponding segment.
// 'd' = decimal, 'h' = hexadeicmal
void displaySeg(unsigned int count, unsigned char flag){

	unsigned char i;
	unsigned int temp;
	unsigned int base;

	if (flag == DEC){
	  base = 10;
	} else if (flag == HEX){
		base = 16;
	}
	// Loop through the 7 segs
	for (i = 0; i < 4; i++){
		switch(i){
			case 0:
				// Take the last digit of the count
				temp = count%base;
				break;

			case 1:
				// Number for the second most right display
				temp = (count/base)%base;
				break;

			case 2:
				// Take the second digit of the count
				temp = (count/(base*base))%base;
				break;

			case 3:
			// Take the first digit of the count
				temp = (count/(base*base*base))%base;
				break;

			default:
				temp = 0x00;
				break;
		  }

		// Convert temp to 7segment
		decimal_to_seg(temp);
		PTP = SEG_MASK[i];
		//delay for some time ( in order to trick the brain into seeing 4 numbers when only 1 7 seg can be on at a time)
		delay();
  }
}


// This function takes a digit and then converts it into 7Segformat and pushes it into PORTB
void decimal_to_seg(unsigned int var){
	if (var < 16){
	  PORTB = NUM_TO_SEG[var];
	}
}


// This function causes a short delay
void delay(void){
	unsigned long count = 100;
	while(count > 0){
		count--;
	}
}
