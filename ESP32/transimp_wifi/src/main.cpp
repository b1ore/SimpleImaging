#include <Arduino.h>
#include <WiFi.h>
#include <touch_trans.h>
#include <adc_trans.h>
#include <swit_trans.h>
#include <string>
//Parameters about scan
#define CHAN_NUM 4
#define PIXEL_NUM 16

#ifndef TIMES
#define TIMES 8
#endif

uint8_t channels[CHAN_NUM] = {CHAN_0, CHAN_1, CHAN_2, CHAN_3};

uint8_t is_scan_on = 0; //0: off, 1: on

WiFiServer server(80, 1);
const char *ssid = "esp32";
const char *password = "12345678";
//这里不设置密码

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 Test"); //println后面加上"\r\n"
  Adc_Init();
  Serial.println("ADC is initialized.");
  Swit_Init();
  Serial.println("SWIT is initialized.");


  //wifi ap模式，模块做客户端
  WiFi.softAP(ssid, password);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);
  server.begin();
  Serial.println("Server started!");

}

void loop() {
  // put your main code here, to run repeatedly:
  WiFiClient client = server.available();
  if (client){
      Serial.print("Client local address: ");
      Serial.println(client.remoteIP());
      Serial.print("Client local port: ");
      Serial.println(client.remotePort());
  }
  uint8_t i, j;
  uint16_t temp;
  while (client.connected()){
    delay(10);
    if (touch_scan(TOUCH_0)){ //
      is_scan_on ^= 1;
    }
    if (is_scan_on){
        for (i = 0; i < CHAN_NUM; i++){
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
          if (touch_scan(TOUCH_0)) is_scan_on ^= 1; //提高触摸pin的灵敏度
        }
    }
  }
}