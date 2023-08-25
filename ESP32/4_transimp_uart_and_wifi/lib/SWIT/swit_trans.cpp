#include <swit_trans.h>

void Swit_Init(){
    // set the mode for pins
    pinMode(SWIT_0, OUTPUT);
    pinMode(SWIT_1, OUTPUT);
    pinMode(SWIT_2, OUTPUT);
    pinMode(SWIT_3, OUTPUT);
}

void Swit_Set(uint8_t pin, uint8_t state){
    digitalWrite(pin, state);
}

void Swit_Reset(){
    //Reset all switchs to OFF state
    digitalWrite(SWIT_0, SWITCH_OFF);
    digitalWrite(SWIT_1, SWITCH_OFF);
    digitalWrite(SWIT_2, SWITCH_OFF);
    digitalWrite(SWIT_3, SWITCH_OFF);
}