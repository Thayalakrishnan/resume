#include <hidef.h>
#include "derivative.h"
#include <math.h>
#include <float.h>
#include <stdio.h>
#include "iic.h"
#include "pll.h"
#include "sci1.h"
//#include "lcd.h"
// #include "keypad.h"
//#include "sevenseg.h"
#include "sensors.h"

 #define BUFFER_SIZE 60

#define BUFF_SIZE 100
#define PI 3.1416
#define MAX_TIMER_COUNT 65536
#define COUNTS_PER_MS 24
#define BUFFER_SIZE 60
#define NEWLINE 0xD
#define ENABLE_RECEIVER 0x0C
#define DISABLE_RECEIVER 0x08
#define CR 0x0D


// Struct for the gyrosocpe
typedef struct {

    int gx;
    int gy;
    int gz;

} GyrSensor;

// Struct for the magnetometer
typedef struct {

    int mx;
    int my;
    int mz;

} MagSensor;

// Struct for the accelerometer values
typedef struct {

    int ax;
    int ay;
    int az;

} AccSensor;

// Struct to keep track of the configuration parameters
typedef struct {

    unsigned short azimuth_min;
    unsigned short azimuth_max;
    unsigned short elevation_min;
    unsigned short elevation_max;
    unsigned short step_size;
    unsigned short scan_frequency;
    unsigned char samples_per_orientation;

    unsigned char is_quickscan;
    unsigned char is_customscan;
    unsigned char is_deepscan;
    unsigned char is_offline_quickscan;
    unsigned char is_offline_customscan;
    unsigned char is_offline_deepscan;
    unsigned char currently_scanning;

} ScanConfig;

// Struct to keep track of the the PTU's movement
typedef struct {

    unsigned short current_azimuth;
    unsigned short current_elevation;
    char current_direction;

} PanandTilt;

// Struct to keep track of the measurable values
typedef struct {

    unsigned short current_azimuth;
    unsigned short current_elevation;
    unsigned short measured_distance;
    unsigned short measured_heading_radians;
    unsigned short measured_heading;
    unsigned short measured_pitch_radians;
    unsigned short measured_pitch;
    unsigned short measured_x;
    unsigned short measured_y;
    unsigned short measured_z;
    
} ScanValues;

volatile unsigned char overflow_counter;
volatile unsigned short rising;
volatile unsigned short distance;
volatile unsigned short average_distance;
volatile unsigned short standard_deviation;
volatile unsigned short azimuth_index;
volatile unsigned short elevation_index;
volatile unsigned short ptu_direction;
volatile unsigned short standard_deviation;
volatile unsigned short i,j,pwm_min,pwm_max, min_j, max_j;
volatile unsigned int direction;

//lidar
char buff[BUFF_SIZE]; 

/* Global Variables */
char buffer[BUFFER_SIZE];
int newline = 0;
int string_position;

int gxraw[BUFF_SIZE];
int gyraw[BUFF_SIZE];
int gzraw[BUFF_SIZE];

int axraw[BUFF_SIZE];
int ayraw[BUFF_SIZE];
int azraw[BUFF_SIZE];

int mxraw[BUFF_SIZE];
int myraw[BUFF_SIZE];
int mzraw[BUFF_SIZE];

// Lidar functions
void get_distance(void);
void pulse_width_measure(void);
void init_lidar(void);

// 
void set_default(void);
void pwm_init(void);
void ptu_move(void);
void configure_scan(void);
void print_results(void);

// Serial
void input_configuration(void);
void configure_custom(char type, int position);
short int capture_bounds(int j);
short int ascii_to_decimal(char character);
void check_confirm(void);

// Gyr Functions
void gyroscope_get(int *gxraw, int *gyraw, int *gzraw);
void gyroscope_init(void);
void gyroscope_test(void);

// Mag Functions
void magnetometer_init(void);
void magnetometer_get(void);
int magnetometer_heading(void);

// Acc Functions
void accelerometer_get(void);
void accelerometer_init(void);
void accelerometer_test(void);

extern ScanConfig configuration;
extern PanandTilt ptu;
extern ScanValues sample;
extern MagSensor magnetometer;
extern AccSensor accelerometer;

void main(void){
  // set default scan . untick this if user selects anything else
  configuration.is_deepscan = 1;

  // snaking from top left corner to bottom right corner
  ptu.current_azimuth = configuration.azimuth_min;
  ptu.current_elevation = configuration.elevation_max;
  ptu.current_direction = 1;

  PLL_Init();
  init_lidar();
  SCI1_Init(BAUD_9600);
  SCI1_OutString("Program Starting ");
  iicinit();
  pwm_init();

  accelerometer_init();
  magnetometer_init();

  EnableInterrupts;
  for(;;){
    input_configuration();
    configure_scan();
    while (configuration.currently_scanning==1){
        sample.measured_distance = 0;
        ptu_move();
        while(sample.measured_distance==0){
            get_distance();
        }
        accelerometer_get();
        magnetometer_get();
        print_results();
    }

  }
}

// Set default scan parameters
void set_default(void){
    configuration.azimuth_min = 2700;
    configuration.azimuth_max = 6300;
    configuration.elevation_min =  2700;
    configuration.elevation_max = 6300;
    configuration.step_size = 25;
    configuration.scan_frequency = 6300;
    configuration.samples_per_orientation = 5;
}

void configure_scan(void){
    
    if (configuration.is_customscan){
        //configuration.azimuth_min = 2700+((configuration.azimuth_min-30)*27.69);
        //configuration.azimuth_max = 6300-((160-configuration.azimuth_max )*27.69);
        //configuration.elevation_min =  2700+((configuration.elevation_min+60)*30);
        //configuration.elevation_max = 6300-((60-configuration.elevation_max)*30);
        return;
    }
    if (configuration.is_quickscan){
        return;
    }
    if (configuration.is_offline_customscan){
        return;
    }
    if (configuration.is_offline_deepscan){
        return;
    }
    if (configuration.is_offline_quickscan){
        return;
    }
    if (configuration.is_deepscan){
        configuration.azimuth_min = 2700;
        configuration.azimuth_max = 6300;
        configuration.elevation_min =  2700;
        configuration.elevation_max = 6300;
        configuration.step_size = 25;
        configuration.scan_frequency = 6300;
        configuration.samples_per_orientation = 5;
        return;
    }
}


void print_results(void){
    DisableInterrupts;
    if(sample.measured_pitch < 0){
        SCI1_OutString("-");
    }
    SCI1_OutUDec((unsigned short) sample.measured_pitch);
    SCI1_OutString(",");
    SCI1_OutUDec((unsigned short) sample.measured_heading);
    SCI1_OutString(",");
    SCI1_OutUDec((unsigned short) sample.current_azimuth);
    SCI1_OutString(",");
    SCI1_OutUDec((unsigned short) sample.current_elevation);
    SCI1_OutString(",");
    SCI1_OutUDec((unsigned short) sample.measured_distance);
    SCI1_OutString("\r\n");
    EnableInterrupts;
}

/*
/// This function calculates the orientation of the magnometer
///
/// Saves the result in heading. The result includes a calibration coefficient
void calculate_orientation_magno(void){
 //12.66 is the magnetic declination value for sydney
  //also added a coeff for calibration
  heading = atan2(mzraw[0],mxraw[0])*(RAD2DEG) - 12.66;
  heading = 90 - heading;
}


/// This function creates a delay for the PWM
///
/// Makes a delay for 50000*10000 cycles
void pwm_delay(void){
	unsigned short count_two = 50000;
	unsigned short count_one = 10000;
	while(count_one > 0){
	  while(count_two> 0){
	     	count_two--;
	  }
	  count_one--;
	}
}
*/

/// This function checks if the timer has overflowed
///
/// This is interrupt based, and it will increment a counter
interrupt 16 void ISR_TIMER_OVERFLOW(void){
    TCNT;
    overflow_counter++;
}

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
        ptu.current_azimuth = configuration.azimuth_max;
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
        ptu.current_azimuth = configuration.azimuth_min;
        ptu.current_azimuth = 1;
        ptu.current_elevation -=configuration.step_size;
        PWMDTY5 = (ptu.current_elevation & 0xFF);
        PWMDTY4 = (ptu.current_elevation >> 8);
      }
    }
  EnableInterrupts;
  }
}

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
  flt_average = flt_sum_distance/index_i;
  
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
      //configuration.

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

      no = 0;
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

//---------------------------------------------------------------------------------
// Magnotomter 
//---------------------------------------------------------------------------------

// Magnetometer initialisation
void magnetometer_init(void){
    int  temp;
    temp=iicstart(magnet_wr);
    temp=iictransmit(HM5883_MODE_REG);
    temp=iictransmit(0x00);
    iicstop();
}

// Magnetormeter acquire
void magnetometer_get(void){
    uint8_t i = 0;
    uint8_t buff[6];
    int temp;
        
    temp=iicstart(magnet_wr);
    temp=iictransmit(HM5883_DATAX0 );
    temp= iicrestart(magnet_rd); 
    iicswrcv();
    
    for(i=0; i<4  ;i++) {
        buff[i]=iicreceive();
    }
    
    buff[i]= iicreceivem1();
    buff[i+1]= iicreceivelast();

    magnetometer.mx = ((buff[0] << 8) | buff[1]);// converts measurement from 2 , store them in struct 
    magnetometer.my = ((buff[2] << 8) | buff[3]);// converts measurement from 2 , store them in struct 
    magnetometer.mz = ((buff[4] << 8) | buff[5]);// converts measurement from 2 , store them in struct 
}

int magnetometer_heading(void){
    volatile float mag_y, mag_z;
    volatile float mag_heading;

    magnetometer_get();
    mag_heading = atan2((float)magnetometer.mz, (float)magnetometer.my);
    return (int)(mag_heading);
}


//---------------------------------------------------------------------------------
// Gyroscope
//---------------------------------------------------------------------------------

// Gyroscope test
// test the precense of Gyro , should get 211 on return
void gyroscope_test(void) {
    int temp,who; 
    
    temp=iicstart(0xD2);
    temp=iictransmit(L3G4200D_WHO_AM_I);
    
    temp=iicrestart(0xD3);
    who=iicreceiveone();
    //who=who & 0x00ff;     Debugging  info
    //PORTB=  who ;
}

//  Gyroscope Initialisation
void gyroscope_init (void) {
    int  temp;

    temp=iicstart(gyro_wr);
    temp=iictransmit(L3G4200D_CTRL_REG1);  // ; 100hz, 12.5Hz, Power up
    temp=iictransmit(0x0f );
    iicstop();  
}

// Gyroscope acquire
void gyroscope_get(int *gxraw, int *gyraw, int *gzraw) {
    uint8_t i = 0;
    uint8_t buff[6];
    int temp;

    temp=iicstart(gyro_wr);
    temp=iictransmit(L3G4200D_OUT_XYZ_CONT);
    temp= iicrestart(gyro_rd); 

    iicswrcv();

    for(i=0; i<4  ;i++) {
        buff[i]=iicreceive();
    }

    buff[i]= iicreceivem1();
    buff[i+1]= iicreceivelast();

    *gxraw = ((buff[1] << 8) | buff[0]);
    *gyraw = ((buff[3] << 8) | buff[2]);
    *gzraw = ((buff[5] << 8) | buff[4]);
}

//---------------------------------------------------------------------------------
// Accelerometer
//---------------------------------------------------------------------------------

// Accelerometer initialisation
void accelerometer_init (void){
    int  temp;
    
    temp=iicstart(accel_wr);
    temp=iictransmit(ADXL345_POWER_CTL);
    temp=iictransmit(0x08 );
    
    temp=iictransmit(ADXL345_DATA_FORMAT);
    temp=iictransmit(0x08 );
    iicstop();
}

// Accelerometer acquire
void accelerometer_get(void){
    uint8_t i = 0;
    uint8_t buff[6];
    int temp;
    
    temp=iicstart(accel_wr);
    temp=iictransmit(ADXL345_DATAX0);
    temp= iicrestart(accel_rd); 
    iicswrcv();
    
    for(i=0; i<4  ;i++) {
        buff[i]=iicreceive();
    }
    
    buff[i]= iicreceivem1();
    buff[i+1]= iicreceivelast();

    accelerometer.ax = ((buff[1] << 8) | buff[0]);
    accelerometer.ay = ((buff[3] << 8) | buff[2]);
    accelerometer.az = ((buff[5] << 8) | buff[4]);
}

void accelerometer_pitch(void){
    volatile long int sum_acc_x = 0;
    volatile long int sum_acc_z = 0;
    volatile float acc_x;
    volatile float acc_z;
    volatile float pitch_angle;
    volatile int pitch;
    unsigned char j = 0;

    // loop and get some values for the average 
    for (j = 0; j < 5; j++){
        accelerometer_get();
        sum_acc_x += accelerometer.ax;
        sum_acc_z += accelerometer.az;
    }
    acc_x = (float)(sum_acc_x/5);
    acc_z = (float)(sum_acc_z/5);
    pitch_angle = atan2(acc_x, acc_z);

    pitch = (int)(pitch_angle * 57.29);
    sample.measured_pitch_radians = pitch_angle;
    sample.measured_pitch = pitch;
}

