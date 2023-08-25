#include <Arduino.h>
#include <WiFi.h>
#include <touch_trans.h>
#include <adc_trans.h>
#include <swit_trans.h>
#include <key_trans.h>

//Parameters about scan
#define CHAN_NUM 16
#define PIXEL_NUM 16

#define MODE_UART 0
#define MODE_WIFI_AP 1

#ifndef TIMES
#define TIMES 3
#endif

uint8_t channels[CHAN_NUM] = {CHAN_0, CHAN_1, CHAN_2, CHAN_3, CHAN_4, CHAN_5, CHAN_6, CHAN_7, CHAN_8, CHAN_9, CHAN_10,
    CHAN_11, CHAN_12, CHAN_13, CHAN_14, CHAN_15};

const char* mode_uart = "UART";
const char* mode_wifi_ap = "WIFI AP";
const char* mode_name[2] = {mode_uart, mode_wifi_ap}; 

// STA parameters
uint8_t is_scan_on = 0; //0: off, 1: on
uint8_t mode = MODE_UART;


WiFiServer server(80, 1);
const char *ssid = "esp32";
const char *password = "12345678";


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 16 channels Test"); //println后面加上"\r\n"
  delay(1000);
  Adc_Init();
  Serial.println("ADC is initialized.");
  Swit_Init();
  Serial.println("SWIT is initialized.");
  KEY_Init();
  Serial.println("KEY is initialized.");
  Serial.println("`SWIT1`: press to start the scan or stop the scan");
  Serial.println("`SWIT2`: press to switch the mode");

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
  delay(5);
  uint8_t i, j;
  uint8_t c0, c1, c2, c3;  // 4 bit to set switch
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
  /*---------------------------wifi ap----------------------------------*/
  if (mode == MODE_WIFI_AP){
    WiFiClient client = server.available();
    if (client && mode == MODE_WIFI_AP){
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
                // select the channel
                c0 = ((i >> 0) & 1) == 1 ? SWITCH_ON : SWITCH_OFF;
                c1 = ((i >> 1) & 1) == 1 ? SWITCH_ON : SWITCH_OFF;
                c2 = ((i >> 2) & 1) == 1 ? SWITCH_ON : SWITCH_OFF;
                c3 = ((i >> 3) & 1) == 1 ? SWITCH_ON : SWITCH_OFF;
                Swit_Set(SWIT_0, c0);
                Swit_Set(SWIT_1, c1);
                Swit_Set(SWIT_2, c2);
                Swit_Set(SWIT_3, c3);
                delay(1);
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
  /*---------------------------uart-------------------------------------*/
  if (is_scan_on && mode == MODE_UART){
      for (i = 0; i < CHAN_NUM && is_scan_on; i++){
      // select the channel
      c0 = ((i >> 0) & 1) == 1 ? SWITCH_ON : SWITCH_OFF;
      c1 = ((i >> 1) & 1) == 1 ? SWITCH_ON : SWITCH_OFF;
      c2 = ((i >> 2) & 1) == 1 ? SWITCH_ON : SWITCH_OFF;
      c3 = ((i >> 3) & 1) == 1 ? SWITCH_ON : SWITCH_OFF;
      Swit_Set(SWIT_0, c0);
      Swit_Set(SWIT_1, c1);
      Swit_Set(SWIT_2, c2);
      Swit_Set(SWIT_3, c3);
      delay(1);
      for (j = 0; j < CHAN_NUM; j++){
          temp = get_adc_average(channels[j], TIMES);
          Serial.printf("%d+%d+%d\r\n", i, j, temp);
      }
      key_val = KEY_Scan();
      if (key_val == KEY_SCAN_PRES) is_scan_on ^= 1; 
      else if (key_val == KEY_MODE_PRES){
              mode ^= 1;
              Serial.printf("Current mode is %s/r/n", mode_name[mode]);
              break;
      }
    }
  }
}