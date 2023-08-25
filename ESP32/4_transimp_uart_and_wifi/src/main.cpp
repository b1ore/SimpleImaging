#include <Arduino.h>
#include <WiFi.h>
#include <touch_trans.h>
#include <adc_trans.h>
#include <swit_trans.h>
#include <key_trans.h>
#include <string>

//Parameters about scan
#define CHAN_NUM 4
#define PIXEL_NUM 16

#define MODE_UART 0
#define MODE_WIFI_AP 1

#ifndef TIMES
#define TIMES 8
#endif

uint8_t channels[CHAN_NUM] = {CHAN_0, CHAN_1, CHAN_2, CHAN_3};
const char* mode_uart = "UART";
const char* mode_wifi_ap = "WIFI AP";
const char* mode_name[2] = {mode_uart, mode_wifi_ap}; 

// STA parameters
uint8_t is_scan_on = 0; //0: off, 1: on
uint8_t mode = MODE_WIFI_AP;

WiFiServer server(80, 1);
const char *ssid = "esp32";
const char *password = "12345678";

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 4 channels Test"); //println后面加上"\r\n"
  Adc_Init();
  Serial.println("ADC is initialized.");
  Swit_Init();
  Serial.println("SWIT is initialized.");
  Serial.println("`SWIT1`: press to start the scan or stop the scan");
  Serial.println("`SWIT2`: press to switch the mode");
  KEY_Init();
  Serial.println("KEY is initialized.");

  //wifi ap模式，模块做客户端
  WiFi.softAP(ssid, password, 1, 0, 1);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);
  Serial.println();
  server.begin();
  Serial.println("Server was started!");
  Serial.println("Available mode: `UART` and `WIFI AP`");
  Serial.printf("Current mode is %s, press `SWIT2` to switch mode.\r\n", mode_name[mode]);
  

}

void loop() {
  // put your main code here, to run repeatedly:
  delay(10);
  uint8_t i, j;
  uint16_t temp;
  uint8_t key_val;
  uint8_t delay_time = 0;
  key_val = KEY_Scan();
  if (key_val == KEY_MODE_PRES){
    mode ^= 1;
    Serial.printf("Current mode is %s\r\n", mode_name[mode]);
  }else if (key_val == KEY_SCAN_PRES){ 
    is_scan_on ^= 1;
  }
  /*-------------------------wifi ap------------------------------*/
  if (mode == MODE_WIFI_AP){
    WiFiClient client = server.available();
    if (client){
        Serial.print("Client local address: ");
        Serial.println(client.remoteIP());
        Serial.print("Client local port: ");
        Serial.println(client.remotePort());
        while (client.connected() && mode == MODE_WIFI_AP){
          delay(5);
          key_val = KEY_Scan();
          if (key_val == KEY_SCAN_PRES) is_scan_on ^= 1; 
          else if (key_val == KEY_MODE_PRES){
            mode ^= 1;
            Serial.printf("Current mode is %s/r/n", mode_name[mode]);
          }
          if (is_scan_on && mode == MODE_WIFI_AP){
              for (i = 0; i < CHAN_NUM && is_scan_on; i++){
                Swit_Reset();
                //选通行
                switch(i){
                  case 0: Swit_Set(SWIT_0, SWITCH_ON);
                          break;
                  case 1: Swit_Set(SWIT_1, SWITCH_ON);
                          break;
                  case 2: Swit_Set(SWIT_2, SWITCH_ON);
                          break;
                  case 3: Swit_Set(SWIT_3, SWITCH_ON);
                          break;
                }
                for (j = 0; j < CHAN_NUM; j++){
                    temp = get_adc_average(channels[j], TIMES);
                    client.printf("%d+%d+%d\r\n", i, j, temp);
                }
                key_val = KEY_Scan(); // 5 ms
                if (key_val == KEY_SCAN_PRES) is_scan_on ^= 1; 
                else if (key_val == KEY_MODE_PRES){
                    mode ^= 1;
                    Serial.printf("Current mode is %s/r/n", mode_name[mode]);
                }
              }
          }
        }
    }
    
  }
  /*----------------UART------------------------------------------*/
    if (is_scan_on && mode == MODE_UART){
      for (i = 0; i < CHAN_NUM && is_scan_on; i++){
        Swit_Reset();
        //选通行
        switch(i){
          case 0: Swit_Set(SWIT_0, SWITCH_ON);
                  break;
          case 1: Swit_Set(SWIT_1, SWITCH_ON);
                  break;
          case 2: Swit_Set(SWIT_2, SWITCH_ON);
                  break;
          case 3: Swit_Set(SWIT_3, SWITCH_ON);
                  break;
        } 
        for (j = 0; j < CHAN_NUM; j++){
            temp = get_adc_average(channels[j], TIMES);
            Serial.printf("%d+%d+%d\r\n", i, j, temp);
        }
        key_val = KEY_Scan(); // 5 ms
        if (key_val == KEY_SCAN_PRES) is_scan_on ^= 1; 
        else if (key_val == KEY_MODE_PRES){
              mode ^= 1;
              Serial.printf("Current mode is %s/r/n", mode_name[mode]);
              break;
        }
      }
  } 
}