#ifndef serialcontrol_H
#define serialcontrol_H

void input_configuration(void);
void configure_custom(char type, int position);
short int capture_bounds(int j);
short int ascii_to_decimal(char character);
void check_confirm(void);

#endif