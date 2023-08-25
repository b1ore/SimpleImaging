#include <key_trans.h>

void KEY_Init(){
    pinMode(KEY1, INPUT_PULLUP);
    pinMode(KEY2, INPUT_PULLUP);
}


uint8_t KEY_Scan(){
    // don't support continuous press
    static uint8_t key_up = 1;
    if (key_up && (KEY_SCAN == LOW || KEY_MODE == LOW)){
        delay(10);
        key_up = 0;
        if (KEY_SCAN == LOW) return KEY_SCAN_PRES;
        else if (KEY_MODE == LOW) return KEY_MODE_PRES;
    }else if (KEY_SCAN == HIGH && KEY_MODE == HIGH) key_up = 1;
    return 0; //no key press
}