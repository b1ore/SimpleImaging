#pragma once
#include <Arduino.h>
/* This document is about ADC module*/

// Here we use 16 channels of ADC1
#define ADC1_CHAN_0 36
#define ADC1_CHAN_3 39
#define ADC1_CHAN_6 34
#define ADC1_CHAN_7 35
#define ADC1_CHAN_4 32
#define ADC1_CHAN_5 33
#define ADC1_CHAN_8 25
#define ADC2_CHAN_9 26
#define ADC2_CHAN_7 27
#define ADC2_CHAN_6 14
#define ADC2_CHAN_5 12
#define ADC2_CHAN_4 13
#define ADC2_CHAN_0 4
#define ADC2_CHAN_1 0
#define ADC2_CHAN_2 2
#define ADC2_CHAN_3 15

// redefine 4 channels for this experiment
#define CHAN_15 ADC1_CHAN_0
#define CHAN_14 ADC1_CHAN_3
#define CHAN_13 ADC1_CHAN_4
#define CHAN_12 ADC1_CHAN_5
#define CHAN_11 ADC1_CHAN_6
#define CHAN_10 ADC1_CHAN_7
#define CHAN_9 ADC1_CHAN_8
#define CHAN_8 ADC2_CHAN_0
#define CHAN_7 ADC2_CHAN_1
#define CHAN_6 ADC2_CHAN_2
#define CHAN_5 ADC2_CHAN_3
#define CHAN_4 ADC2_CHAN_4
#define CHAN_3 ADC2_CHAN_5
#define CHAN_2 ADC2_CHAN_6
#define CHAN_1 ADC2_CHAN_7
#define CHAN_0 ADC2_CHAN_9

void Adc_Init(void);
uint16_t get_adc_average(uint8_t chan, uint8_t times);



