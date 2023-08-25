#pragma once
#include <Arduino.h>
/*This decument is about switch control*/

//define switch pin
#define SWIT_0 23
#define SWIT_1 22
#define SWIT_2 19
#define SWIT_3 18

#define SWITCH_ON HIGH
#define SWITCH_OFF LOW

void Swit_Init(void);
void Swit_Set(uint8_t swit,  uint8_t state);

void Swit_Reset(void);