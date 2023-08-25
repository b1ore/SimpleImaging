#pragma once
// This document is about key
#include <Arduino.h>

#define KEY1 23   // switch mode
#define KEY2 22

#define KEY_SCAN digitalRead(KEY1)
#define KEY_MODE digitalRead(KEY2)

#define KEY_SCAN_PRES 1
#define KEY_MODE_PRES 2

void KEY_Init(void);
uint8_t KEY_Scan(void);

