#pragma once
#include <Arduino.h>
/* This document is about ADC module*/

// Here we use 4 channels of ADC1
#define ADC1_CHAN_0 36
#define ADC1_CHAN_3 39
#define ADC1_CHAN_4 32
#define ADC1_CHAN_5 33
#define ADC1_CHAN_6 34
#define ADC1_CHAN_7 35

// redefine 4 channels for this experiment
#define CHAN_0 ADC1_CHAN_0
#define CHAN_1 ADC1_CHAN_3
#define CHAN_2 ADC1_CHAN_4
#define CHAN_3 ADC1_CHAN_5

void Adc_Init(void);
uint16_t get_adc_average(uint8_t chan, uint8_t times);



