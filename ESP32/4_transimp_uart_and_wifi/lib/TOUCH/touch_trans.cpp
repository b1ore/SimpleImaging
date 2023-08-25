#include <touch_trans.h>

uint8_t touch_scan(uint8_t pin){
    // not allow continous touch
    // return: 1, successful touch; 0, failed touch
    static uint8_t TOUCH_LOCK = TOUCH_ON; // 'on' allow touch to work
    if (TOUCH_LOCK == TOUCH_ON && touchRead(pin) <= TOUCH_THRES){
      delay(10); //去抖动
      TOUCH_LOCK = TOUCH_OFF;
      return 1;
    }
    else if (touchRead(pin) > TOUCH_THRES) TOUCH_LOCK = TOUCH_ON; //松手打开lOCK
    return 0;
}