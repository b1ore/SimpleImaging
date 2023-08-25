#pragma once

/*This document is about TOUCH module*/
/*不支持连续触摸*/
#include <Arduino.h>
#define TOUCH_0 4    //touch pin
#define TOUCH_THRES 16   // threshold to judge whether the pin is touched
#define TOUCH_ON 1
#define TOUCH_OFF 0

uint8_t touch_scan(uint8_t pin);
