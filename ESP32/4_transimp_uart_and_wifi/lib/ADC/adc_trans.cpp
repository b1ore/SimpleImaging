#include <adc_trans.h>

void Adc_Init(){

    //Attch ADC to pins
    adcAttachPin(CHAN_0);
    adcAttachPin(CHAN_1);
    adcAttachPin(CHAN_2);
    adcAttachPin(CHAN_3);

    //Set attenuation
    analogSetAttenuation(ADC_11db);

    //Set read resolution
    analogReadResolution(12);

}


uint16_t get_adc_average(uint8_t chan, uint8_t times){
    if (times >= 16){ //防止overflow,这里配合12位的读取精度
        times = 16;
    }
    uint16_t res = 0;
    uint8_t i;
    for (i = 0; i < times; i++){
        delay(2);
        res += analogRead(chan);
    }
    return res / times;
}