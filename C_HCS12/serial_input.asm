;********************************************************************************
;* Program that reads serial input and outputs it to the LEDs                   *
;* - Board is running at 24 Mhz (41.6n sec)                                     *
;* - Dragon_12: A. Taras, L. Thayalkrishnan, J. Sun, J. Tran                    *
;*   18/03/20                                                                   *
;* - Functions:                                                                 *
;*   - initialisation                                                           *
;* - Last Modification: 22/03/20  Coding documentation and explanations         *
;********************************************************************************

; export symbols
            XDEF Entry, _Startup            ; export 'Entry' symbol
            ABSENTRY Entry                  ; for absolute assembly: mark this as application entry point



; Include derivative-specific definitions
		INCLUDE 'derivative.inc'

ROMStart    EQU  $4000                      ; absolute address to place my code/constant data

; variable/data section

            ORG RAMStart

; Insert your data definitiosn here
RDRF        DS.W $80  ; Used to check if receiver is ready
SetHigh     EQU $FF   ; Set bits to '11111111'
SetLow      EQU $00   ; Set bits to '00000000'
segOff      EQU $0F   ; These selected bits '11110000' turn off the 7 segments

; code section
            ORG   ROMStart

Entry:
_Startup:
            LDS   #RAMEnd+1         ; initialize the stack pointer
            CLI                     ; enable interrupts
mainLoop:
            BSR configuration       ; first configure the SCI

inputRead:
            BRCLR SCI1SR1,#mSCI1SR1_RDRF,*  ; check if the receive flag is triggered
            MOVB SCI1DRL,PORTB      ; if the receive flag has been set, move the value in the data register to port b
            BRA inputRead           ; branch to the back to subroutine 'inputRead'

;**************************************************************
;*                       Configuration                        *
;*                                                            *
;* - Used to initalise all the control registers, setting:    *
;*   the baud rate, 8 or 9 bits per character, parity and     *
;*   we are transmitting or receiving. This function also     *
;*   setups the LEDs for output                               *
;* - 24MHz clock (41.66 ns)                                   *
;* - Last Updated: 22/03/2020                                 *
;**************************************************************
configuration:
            MOVB #SetLow,SCI1BDH    ; we would set these for higher BRs. also important to write to this first
            MOVB #$9C,SCI1BDL       ; set the baud rate to 9600 (decimal 1566)
            MOVB #SetLow,SCI1CR1   ; set 8 data bits, no parity
            MOVB #$04,SCI1CR2       ; set the 2nd bit high, this enables the receiver

            MOVB #SetHigh,DDRB      ; configure DDRB for input
            MOVB #SetHigh,DDRJ      ; configure leds
            MOVB #SetLow,PTJ        ; set other line of LEDs low to drive with PTP

                                    ; also turn 7 segs off because it looks funny
            MOVB #SetHigh,DDRP      ; configure 7seg for output
            MOVB #$0F,PTP           ; set mask to never enable 7 seg
            RTS                     ; return from subroutine

;**************************************************************
;*                 Interrupt Vectors                          *
;**************************************************************
            ORG   $FFFE
            DC.W  Entry           ; Reset Vector
