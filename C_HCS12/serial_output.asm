;********************************************************************************
;* Program that takes two strings and sends them out of the port at a rate of   *
;* one message every second                                                     *
;* - Board is running at 24 Mhz (41.6n sec)                                     *
;* - Dragon_12: A. Taras, L. Thayalkrishnan, J. Sun, J. Tran                    *
;*   18/03/20                                                                   *
;* - Functions:                                                                 *
;*   - delay                                                                    *
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
;**************************************************************
;*                     Data Definitions                       *
;* $0A = new line                                             *
;* $0D = carraige return                                      *
;**************************************************************

FirstString             dc.b "The Sentence Below is False",$0D,$0A,$00
SecondString            dc.b "The Sentence Above is True",$0D,$0A,$00

StringSwitch            EQU $02
EndOfString             EQU $00
EnableTransmission      EQU $08
SetHigh                 EQU $FF   ; Set bits to '11111111'
SetLow                  EQU $00   ; Set bits to '00000000'
BaudConfig              EQU $9C   ; Set baud rate to 9600
DelaySize               EQU 8001     

;**************************************************************
;**************************************************************
;*                           Main                             *
;**************************************************************
;**************************************************************
            ORG   ROMStart

Entry:
_Startup:
            LDS   #RAMEnd+1         ; initialize the stack pointer
            CLI                     ; enable interrupts
mainLoop:
            BSR configuration       ; first configure the SCI

switcher:
            LDAB #StringSwitch      ; reg b will keep track of which string we are currently on
            LDX #FirstString        ; reg X will point to the address of the first string

printString:
            LDAA X                  ; load the first elment in the first string
            STAA SCI1DRL            ; send  this character to be outputted
            BRCLR SCI1SR1,#mSCI1SR1_TDRE,*  ; wait until the transmit flag is cleared
            INX                     ; move to next character
            CMPA #EndOfString       ; check if we are at the end of a string
            BNE printString         ; loop if not null char

            BSR delay               ; run a delay - dont know if we need this
            LDX #SecondString
            DBEQ b,switcher         ; decrease reg b, if b is zero, we have gone through both strings, so restart
            BRA printString         ; if not, keep printing the string
 
;**************************************************************
;*                       Initialistaion                       *
;*                                                            *
;* - Used to initialise the controls registers: setting the   *
;*   baud rate, 8 or 9 bits, parity, and whether it is        *
;*   receiving or transmitting                                *
;* - 24MHz clock (41.66ns)                                    *
;* - Last Updated 22/03/2020                                  *
;**************************************************************
configuration:
            MOVB #SetLow,SCI1BDH                   ; we would set these for higher BRs. also important to write to this first
            MOVB #BaudConfig,SCI1BDL               ; set the baud rate to 9600
            MOVB #SetLow,SCI1CR1                   ; set 8 data bits low, no parity
            MOVB #EnableTransmission,SCI1CR2       ; set the 3rd bit high, this enables transmission
            RTS

;**************************************************************
;*                           Delay                            *
;*                                                            *
;* - This function generates a 1ms delay using register x     *
;* - 24MHz clock (41.66ns per cycle)                          *
;* - Last updated: 22/03/20                                   *
;* - Calculations:                                            *
;*   Total cycles = Desired Delay/41.66n                      *
;*   Loop(x)      = Total cycles/3 - overhead                 *
;*   Overhead     = (2 + 5)*41.66ns                           *
;**************************************************************
delay:
            LDY #122        ; 2 cyc load matlab value into y
outerLoop:  LDX #65535      ; 2 cyc load matlab value into X
innerLoop:  DBNE x,innerLoop; 3 cyc branch if =/= 0, repeats this line 
            DBNE y,outerLoop; 3 cyc branch if =/= 0
            RTS             ; 5 cyc return from subroutine   

;**************************************************************
;*                 Interrupt Vectors                          *
;**************************************************************
            ORG   $FFFE
            DC.W  Entry           ; Reset Vector
