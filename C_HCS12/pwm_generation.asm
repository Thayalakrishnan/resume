;********************************************************************************
;* - Generates a PWM signal based on the serial input from the computer.        *
;*   The input is taken as strings which duty cycle                             *.
;*==============================================================================*
;*       |Duty Cycle| %                                                         *
;*            v v                                                               *
;*   Input: [c][c][c][c][c]                                                     *
;*                 ^  ^  ^                                                      *
;*                 |Period| ms                                                  *
;*==============================================================================*
;* - Board is running at 24 Mhz (41.6n sec)                                     *
;* - Dragon_12: A. Taras, L. Thayalkrishnan, J. Sun, J. Tran                    *
;*   08/04/20                                                                   *
;* - Functions:                                                                 *
;*   - sciIsr                                                                   *
;*   - sciISrend                                                                8
;*   - resetCounter                                                             *
;*   - processFirstLetter                                                       *
;*   - processSecondLetter                                                      *
;*   - processThirdLetter                                                       *
;*   - processFourthLetter                                                      *
;*   - processFifthLetter                                                       *
;*   - updatePeriod                                                             *
;*   - oscir                                                                    *
;*   - moveToHigh                                                               *
;*   - moveToLow                                                                *
;*   - getNumCycLow                                                             *
;*   - getNumCycHigh                                                            *
;* - Last Modification: 7/04/20  Coding documentation and explanations          *
;********************************************************************************

; export symbols
            XDEF Entry, _Startup            ; export 'Entry' symbol
            ABSENTRY Entry                  ; for absolute assembly: mark this as application entry point

; Include derivative-specific definitions
		INCLUDE 'derivative.inc'

ROMStart    EQU  $4000                      ; absolute address to place my code/constant data


; variable/data section
 ifdef _HCS12_SERIALMON
            ORG $3FFF - (RAMEnd - RAMStart)
 else
            ORG RAMStart
 endif

; code section
            ORG   ROMStart


Entry:
_Startup:

;* ------------------------------------
;* Global variables

; Period

; MEMORY
state        EQU   $1050            ; ask for 1 byte of memory, 0 is LOW, 1 is HIGH
nextCycles   EQU   $1051            ; 2 bytes, stores the number of cycles for the next cycle
charCounter  EQU   $1053            ; 1 byte, memory used to store the count of the number of characters
period       EQU   $1054            ; 2 bytes, full period (in timer cycles)
periodMs     EQU   $1056            ; 2 bytes, full period (in ms)
dutyCycle    EQU   $1058            ; 2 bytes, duty cycle as a HEX percentage

; CONSTANTS
LED_ON       EQU   $01              ; required bits to turn on the LED
LED_OFF      EQU   $00              ; required bits to turn off the LED
msToCycles   EQU   187              ; =24e6/(128 x 1e3)
asciiToDec   EQU   $30              ; number to subtract
newline      EQU   $D               ; equivalent hexadecimal for a newline character
SetLow       EQU   $00              ; bit 00000000
SetHigh      EQU   $FF              ; bit 11111111

;  Frequency 24/32 Mhz

; ------------------------------------
; Main program


; Configure registers
            SEI                       ; disable all interrupts
            MOVB        #$01,TCTL1    ; set up output to toogle
            MOVB        #$10,TIOS     ; select channel 4 for Output compare
            MOVB        #$90,TSCR1    ; enable timers   #$90 does not req Flag cleared
            MOVB        #$07,TSCR2    ; prescaler  div 32
            BSET        TIE,#$10      ; enable Timer Interrupt 4
            JSR         configuration ; jump to subroutine configuration

            MOVB #00, charCounter     ; set the char counter to zero

; Initialising the following values
            MOVW #150, periodMs       ; initialising periodMs to 150
            MOVB #50, dutyCycle       ; initialising dutyCycle to 50
            MOVB #01, charCounter     ; initalising character counter to 01

            JSR updatePeriod          ; jump to subroutine updatePeriod


; set LED for on period
            LDAB PTH                  ; load DIP value into acc B

            JSR getNumCycHigh         ; load Y with number of cycles

            LDD         TCNT          ; get current count and put it in D
            ADDD        Y             ; add number of cycles Y + D -> D
            STD         TC4           ; reload TOC2 with D

            MOVB #$01, state          ; set state to 1
            MOVB #LED_ON, PORTB       ; Turn LED on

; then turn on interrupt
            CLI                       ;enable all interrupts

; Infinite Loop
loop:       BRA  *

;*********************************************************
;*                     sciIsr                            *
;* - Read inputs then changes values of memory according *
;*   to what character it is                             *
;* - Checks if it is one of the 5 characters assigned or *
;*   a newline character. If not, it just ignores the    *
;*   input                                               *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 08/04/2020                             *
;*********************************************************
sciIsr:
            LDAA SCI1SR1              ; allows the TDRE flag to be reset
            LDAA charCounter          ; load what character is being read into A

            LDAB SCI1DRL              ; load B with SCI value
            CMPB #newline             ; check if it is a newline character
            BEQ resetCounter          ; if it is branch to reset counter subroutine

            CMPA #01                  ; check if on first letter
            BEQ processFirstLetter    ; branch to appropriate sr

            CMPA #02                  ; check if on second letter
            BEQ processSecondLetter   ; branch to appropriate sr

            CMPA #03                  ; check if on third letter
            BEQ processThirdLetter    ; branch to appropriate sr

            CMPA #04                  ; check if on fourth letter
            BEQ processFourthLetter   ; branch to appropriate sr

            CMPA #05                  ; check if on fifth letter
            BEQ processFifthLetter    ; branch to appropriate sr

;*********************************************************
;*                     sciIsrEnd                         *
;* - Increments the character rounter, then returns from *
;*   interrupt                                           *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 08/04/2020                             *
;*********************************************************
sciIsrEnd:  INC charCounter           ; increments the content by 1 at memory location charCounter
            RTI                       ; return from interrupt

;*********************************************************
;*                     resetCounter                      *
;* - Resets the character counter to 1(after inc in ISR) *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 08/04/2020                             *
;*********************************************************
resetCounter:
            MOVB #00, charCounter     ; reset counter to 0
            BRA sciIsrEnd             ; return to the end of the interrupt

;*********************************************************
;*               processFirstLetter                      *
;* - 'Tens' digit of the duty cycle                       *
;* - Sets the duty cycle to ten times the input number   *
;* - Input: [c][c][c][c][c]                              *
;*           ^                                           *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 08/04/2020                             *
;*********************************************************
processFirstLetter:
            LDAB SCI1DRL              ; load B with SCI value
            SUBB #asciiToDec          ; convert to actual number
            LDAA #10                  ; load A with 10
            MUL                       ; A x B -> A:B  so B has the required number
            STAB dutyCycle            ; store the value in memory
            BRA sciIsrEnd             ; return to the end of the interrupt

;*********************************************************
;*               processSecondLetter                     *
;* - 'Ones' digit of the duty cycle                      *
;* - Sets the duty cycle to the previous duty cycle plus *
;*   this number                                         *
;* - Input: [c][c][c][c][c]                              *
;*              ^                                        *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 08/04/2020                             *
;*********************************************************
processSecondLetter:
            LDAB SCI1DRL              ; load B with SCI value
            SUBB #asciiToDec          ; convert to actual number
            ADDB dutyCycle            ; add tens of duty cycle with B
            STAB dutyCycle            ; store B in memory
            BRA sciIsrEnd             ; return to the end of the interrupt

;*********************************************************
;*               processThirdLetter                      *
;* - 'Hundreds' digit of the period                      *
;* - Mulitplies the digit by 100 and saves it as the     *
;*   period                                              *
;* - Input: [c][c][c][c][c]                              *
;*                 ^                                     *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 08/04/2020                             *
;*********************************************************
processThirdLetter:
            LDAB SCI1DRL              ; load B with SCI value (input)
            SUBB #asciiToDec          ; convert to actual number (B - #asciitoDec)
            LDAA #100                 ; load A with 100
            MUL                       ; A x B -> A:B  so D has the required value of period in ms
            STD periodMs              ; store D into periodMs {memory location}
            BRA sciIsrEnd             ; return to the end of the interrupt

;*********************************************************
;*              processFourthLetter                      *
;* - 'Tens' digit of the period                          *
;* - Mulitplies the digit by 10                          *
;* - Input: [c][c][c][c][c]                              *
;*                    ^                                  *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 08/04/2020                             *
;*********************************************************
processFourthLetter:
            LDAB SCI1DRL              ; load B with SCI value
            SUBB #asciiToDec          ; convert to actual number
            LDAA #10                  ; load A with 10
            MUL                       ; A x B -> A:B  so D has the required value of period in ms
            ADDD periodMs             ; Add content of periodMs to D
            STD periodMs              ; Store D into memory location periodMs
            BRA sciIsrEnd             ; return to the end of the interrupt

;*********************************************************
;*              processFifthLetter                       *
;* - 'Ones' digit of the period                          *
;* - Input: [c][c][c][c][c]                              *
;*                       ^                               *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 08/04/2020                             *
;*********************************************************
processFifthLetter:
            LDAB SCI1DRL              ; load B with SCI value
            SUBB #asciiToDec          ; convert to actual number
            CLRA                      ; clear A to ensure D only holds ones value
            ADDD periodMs             ; Add content of periodMs to D
            STD periodMs              ; Store D into memory location periodMs
            BSR updatePeriod          ; Branch to subroutine updatePeriod (since this is the last digit)
            BRA sciIsrEnd             ; return to the end of the interrupt

;*********************************************************
;*              updatePeriod                             *
;* - Updates the period in timer cycles                  *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 08/04/2020                             *
;*********************************************************
updatePeriod:
            LDD periodMs              ; Load periodMs into D
            LDY #msToCycles           ; Load Y with the conversion, msToCycles
            EMUL                      ; Y x D -> Y:D so D has value we need
            STD period                ; update period into D
            RTS                       ; return from subroutine

; ------------------------------------
; ISR: Output compare event. Set time for NEXT event
; Increment Global Variable and sent to LED (PORTB)

;*********************************************************
;*                     OSCIR                             *
;* - Output compare event. Set time for NEXT event,      *
;*   increment Global Variable and sent to LED (PORTB)   *
;* - Branches to moveToHigh or moveToLow based on if     *
;*   CCRBZ is set. (Only set if result of operation is 0)*
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 07/04/2020                             *
;*********************************************************
ocisr:
            LDAB PTH                  ; load DIP value into acc B
            LDAA state                ; Load current state into A
            BEQ moveToHigh            ; branch to moveToHigh if Z = 1 (if A is equal to 0 (low))
            DECA                      ; if it is not HIGH, is must be low so decrement A
            BEQ moveToLow             ; branch to moveToLow if Z = 1  (if A was high (1), now it would be (low))

;*********************************************************
;*                     ocIsrEnd                          *
;* - Returns from interrupt                              *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 07/04/2020                             *
;*********************************************************
ocIsrEnd:   RTI                       ; return from interrupt

;*********************************************************
;*                   moveToHigh                          *
;* - Loads the timer counter with the number of cycles   *
;*   required for the HIGH portion of the PWM signal     *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 07/04/2020                             *
;*********************************************************
moveToHigh:
            LDAB dutyCycle            ; load B with the duty cycle
            BSR getNumCycHigh         ; load Y with number of cycles

            LDD         TCNT          ; get current count
            ADDD        nextCycles    ; add number of cycles Y + D -> D
            STD         TC4           ; reload TOC2

            MOVB #$01, state          ; set state to 1
            MOVB #LED_ON, PORTB       ; Turn LED on

            BRA ocIsrEnd              ; branch to ocIsrEnd subroutine

;*********************************************************
;*                   moveToLow                           *
;* - Loads the timer counter with the number of cycles   *
;*   required for the LOW portion of the PWM signal      *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 07/04/2020                             *
;*********************************************************
moveToLow:
            LDAB dutyCycle            ; load accumulator B with the duty cycle
            BSR getNumCycLow          ; load Y with number of cycles

            LDD         TCNT          ; get current count
            ADDD        nextCycles    ; add number of cycles Y + D -> D
            STD         TC4           ; reload TOC2

            MOVB #$00, state          ; set state to LOW
            MOVB #LED_OFF, PORTB      ; Turn LED OFF

            BRA ocIsrEnd              ; branch to the respective subroutine


;*********************************************************
;*                getNumCycHigh                          *
;* - Returns the number of cycles required for the HIGH  *
;*   portion of the PWM signal                           *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 07/04/2020                             *
;*********************************************************
getNumCycHigh:
          LDX #$100                   ; load register X with 100
          LDAA #$00                   ; ensure A is low so input is just in B

          FDIV                        ; fractional divide D and X {(D/X = X) remainder = D}

          EXG X,Y                     ; swap X and Y

          LDD period                  ; load D with the period (in cycles)
          EMUL                        ; multiply D and Y {D * Y = D:Y}

          STY  nextCycles             ; store Y for later use

          RTS                         ; return from subroutine

;*********************************************************
;*                getNumCycLow                           *
;* - Returns the number of cycles required for the LOW   *
;*   portion of the PWM signal                           *
;* - 24MHz clock (41.66ns)                               *
;* - Last Updated 07/04/2020                             *
;*********************************************************
getNumCycLow:
          LDAA #$FF
          SBA                         ; subtract acc, result is in B
          EXG A,B                     ; swap A and B

          LDX #$100                   ; kiad register X with 100
          LDAA #$00                   ; ensure A is low so input is just in B {D = B}

          FDIV                        ; fractional divide D and X {(D/X = X) remainder = D}

          EXG X,Y                     ; swap X and Y

          LDD period                  ; load D with the period
          EMUL                        ; multiply D and Y {D * Y = D:Y}

          STY  nextCycles             ; store Y for later use

          RTS                         ; return from subroutine

;**************************************************************
;*                       Configuration                        *
;*                                                            *
;* - Used to initalise all the control registers, setting:    *
;*   the baud rate, 8 or 9 bits per character, parity and     *
;*   we are transmitting or receiving. This function also     *
;*   setups the LEDs for output                               *
;* - 24MHz clock (41.66 ns)                                   *
;* - Last Updated: 08/04/2020                                 *
;**************************************************************
configuration:
            MOVB #SetLow,SCI1BDH    ; we would set these for higher BRs. also important to write to this first
            MOVB #$9C,SCI1BDL       ; set the baud rate to 9600 (decimal 1566)
            MOVB #SetLow,SCI1CR1    ; set 8 data bits, no parity
            MOVB #%00100100,SCI1CR2 ; set the 2nd bit high, this enables the receiver

            MOVB #SetHigh,DDRB      ; configure DDRB for input
            MOVB #SetHigh,DDRJ      ; configure leds
            MOVB #SetLow,PTJ        ; set other line of LEDs low to drive with PTP
            CLR    PORTB            ; clear portB to not display anything

                                    ; also turn 7 segs off because it looks funny
            MOVB #SetHigh,DDRP      ; configure 7seg for output
            MOVB #$0F,PTP           ; set mask to never enable 7 seg
            RTS                     ; return from subroutine

;**************************************************************
;*                 Interrupt Vectors                          *
;**************************************************************
            ORG   $FFFE
            DC.W  Entry           ; Reset Vector

            ; ------------------------------------
; ISR configuration: Timer 4
            org         $FFE6
            DC.W         ocisr

            org         $FFD4
            DC.W         sciIsr
