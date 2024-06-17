#include <Servo.h>
#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <PZEM004Tv30.h>


// SETUP NTP =====================================================================================
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 25200); // 25200 is the UTC+7 offset
// [END] =========================================================================================



// SETUP Servo ====================================================================================
const int servoPin [11] = {13, 12, 14, 27, 26, 25, 33, 32, 35, 34, 5};

// units in degrees per second
double speed = 140.0;

// When easing constant (ke) < 1.0, return value is normalized, when 1.0, returns pulse width (μs)
// ke = 0.0 is linear, between 0.0 and 1.0 is tunable sigmoid, 1.0 is normal response
// Normalized Tunable Sigmoid: https://www.desmos.com/calculator/ejkcwglzd1
// deegre
double ke = 0.0;

// go to position (degrees)
uint8_t pos = 180;

float ye1, ye2;
Servo myservo = Servo();
// [END] =========================================================================================



// Setup Wifi ====================================================================================
const char *ssid = "Dastin Aryo Atmanto";
const char *pass = "123dastinaryo";
int lastRequest = 0;
// [END] =========================================================================================


// Setup Firebase ================================================================================
//Provide the token generation process info.
#include "addons/TokenHelper.h"
//Provide the RTDB payload printing info and other helper functions.
#include "addons/RTDBHelper.h"

// Insert Firebase project API Key
#define API_KEY "AIzaSyBUpK_rPmyscqQWoCIEhonsMJ_wXLyy8h0"

// Insert RTDB URLefine the RTDB URL */
#define DATABASE_URL "https://electrical-project-8def2-default-rtdb.asia-southeast1.firebasedatabase.app/" 

//Define Firebase Data object
FirebaseData fbdo;

FirebaseAuth auth;
FirebaseConfig config;

bool signupOK = false;

char tanggal[15];
char timestamp[10];
char power[5];
char energy[10];
// int temp_token;
String temp_token_str, token_str;
uint64_t temp_token, token;
unsigned long epochTime;
// [END] =========================================================================================


// Setup PZEM-004T ===============================================================================
#define RXD2 16 
#define TXD2 17
PZEM004Tv30 pzem(Serial2, RXD2, TXD2); // Use Serial2 for communication with PZEM004

float voltage1, current1, power1, energy1, temp_energy1,frequency1, pf1, va1, VAR1;
// [END] =========================================================================================


// Setup FreeRTOS ================================================================================
TaskHandle_t servoTaskHandle;
TaskHandle_t firebaseTaskHandle;
TaskHandle_t pzemTaskHandle;
// [END] =========================================================================================

void setupWifi();
void pzemTask(void *parameter);
void firebaseTask(void *parameter);
void servoTask(void *parameter);


void setup() {
  Serial.begin(9600);
  vTaskDelay(1000);

  // Setup Wifi
  setupWifi();
  timeClient.begin();

  /* Assign the api key (required) */
  config.api_key = API_KEY;

  /* Assign the RTDB URL (required) */
  config.database_url = DATABASE_URL;

  /* Sign up */
  if (Firebase.signUp(&config, &auth, "", "")){
    Serial.println("ok");
    signupOK = true;
  }
  else{
    Serial.printf("%s\n", config.signer.signupError.message.c_str());
  }

  /* Assign the callback function for the long running token generation task */
  config.token_status_callback = tokenStatusCallback; //see addons/TokenHelper.h
  
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  // Setup PZEM-004T
  if (pzem.resetEnergy()){
    ESP_LOGI("SETUP PZEM-004T", "Energy Reset...");
    pzem.setPowerAlarm(2200);
  }
  vTaskDelay(1000);
  
  timeClient.update();
  epochTime = timeClient.getEpochTime();

  // Convert epoch time to struct tm
  struct tm *timeinfo;
  timeinfo = localtime((time_t *)&epochTime);
  
  
  snprintf(tanggal, sizeof(tanggal), "%02d-%02d-%04d",
          timeinfo->tm_mday,
          timeinfo->tm_mon + 1,
          timeinfo->tm_year + 1900);

          // Firebase.RTDB.getInt(&fbdo, "/test/int")) 

  if (Firebase.RTDB.getFloat(&fbdo, "/collection_data/electricity data/"+String(tanggal)+"/kwh")){
    temp_energy1 = fbdo.floatData();
    Serial.println("Data: " + String(temp_energy1));
  }else{
    temp_energy1 = 0.0;
  }

  if (Firebase.RTDB.getString(&fbdo, "/collection_data/tokenizer/stroom_token")){
    temp_token_str = fbdo.stringData();

    // Menggunakan fungsi strtoull untuk konversi
    temp_token = strtoull(temp_token_str.c_str(), NULL, 10);

    Serial.println(temp_token_str);
    Serial.println(temp_token);
    // temp_token = fbdo.StringData();
  }
  

  ESP_LOGI("SETUP", "Create freertos task!");
  // Create RTOS task
  xTaskCreate(pzemTask, "PZEM004T Task", 20000, NULL, 1, &pzemTaskHandle);
  xTaskCreate(firebaseTask, "Firebase Task", 65000, NULL, 2, &firebaseTaskHandle);
  xTaskCreate(servoTask, "Servo Task", 40000, NULL, 3, &servoTaskHandle);
}

void loop() {
  if (millis() - lastRequest > 10000) {
      if (WiFi.status() != WL_CONNECTED) {
          setupWifi();
      } else {
          ESP_LOGI("WIFI", "WiFi is already connected...");
      }
      lastRequest = millis();
  }
}

float zeroIfNan(float v) {
  if (isnan(v)) {
    v = 0;
  }
  return v;
}

void setupWifi() {
    vTaskDelay(10);
    // We start by connecting to a WiFi network
    ESP_LOGI("WIFI", "Connecting to %s", ssid);

    WiFi.begin(ssid, pass);

    while (WiFi.status() != WL_CONNECTED) {
        vTaskDelay(500);
        ESP_LOGI("WIFI", ".");
    }
    ESP_LOGI("WIFI", "WiFi is connected!");
}

void pzemTask(void *parameter){
  for (;;) {
    voltage1 = pzem.voltage();
    voltage1 = zeroIfNan(voltage1); // Voltage
    current1 = pzem.current();
    current1 = zeroIfNan(current1); // Current
    power1 = pzem.power();
    power1 = zeroIfNan(power1); // Power Active
    energy1 = pzem.energy();
    energy1 = temp_energy1+zeroIfNan(energy1); // Energy
    frequency1 = pzem.frequency();
    frequency1 = zeroIfNan(frequency1); // Frequency
    pf1 = pzem.pf();
    pf1 = zeroIfNan(pf1); // Cosine Phi

    if (pf1 == 0) {
      va1 = 0;
    } else {
      va1 = power1 / pf1;
    }
    if (pf1 == 0) {
      VAR1 = 0;
    } else {
      VAR1 = power1 / pf1 * sqrt(1 - sq(pf1));
    }
    
    ESP_LOGI("PZEM-004T", "Energy :  %.3f kWh", power1);

    vTaskDelay(3000);
  }
}

void firebaseTask(void *parameter){
  for (;;) {
    // Cara menggabungkan str dan int
    // char timestamp[50];
    // sprintf(timestamp, "%s%d", "23:58:", count);
    timeClient.update();
    epochTime = timeClient.getEpochTime();

    // Convert epoch time to struct tm
    struct tm *timeinfo;
    timeinfo = localtime((time_t *)&epochTime);
    
    
    snprintf(tanggal, sizeof(tanggal), "%02d-%02d-%04d",
           timeinfo->tm_mday,
           timeinfo->tm_mon + 1,
           timeinfo->tm_year + 1900);
    
    snprintf(timestamp, sizeof(timestamp), "%02d:%02d:%02d",
           timeinfo->tm_hour,
           timeinfo->tm_min,
           timeinfo->tm_sec);

    snprintf(power, sizeof(power), "%.2f", power1);

    snprintf(energy, sizeof(energy), "%.4f", energy1);

    if (Firebase.RTDB.setFloat(&fbdo, "collection_data/electricity data/"+String(tanggal)+"/daya", atof(power)) &&
        Firebase.RTDB.setFloat(&fbdo, "collection_data/electricity data/"+String(tanggal)+"/kwh", atof(energy)) &&
        // Firebase.RTDB.setFloat(&fbdo, "collection_data/electricity data/"+String(tanggal)+"/biaya", atof(energy)*1352) &&
        Firebase.RTDB.setString(&fbdo, "collection_data/electricity data/"+String(tanggal)+"/timestamp", timestamp)
    ){
      ESP_LOGI("FIREBASE", "Data successfully to sent");
    }
    else {
      ESP_LOGI("FIREBASE", "Data failed to sent");
    }
    vTaskDelay(10000);
  }
}

void servoTask(void *parameter){
  for (;;) {
    // if (Firebase.RTDB.getString(&fbdo, "/collection_data/tokenizer/stroom_token")){
    //   token_str = fbdo.stringData();
    //   token = strtoull(token_str.c_str(), NULL, 10);
    //   ESP_LOGI("TOKEN", "Token :  %.d", token);
    //   if (token_str != temp_token_str){
    //     for (byte i = 0; i < token_str.length(); i++) {
    //       char digit_str = token_str[i];
    //       int digit = atoi(&digit_str);

    //       Serial.println(digit); // Cetak digit

    //       if (ye1 <= 0.0 ) pos = 180;
    //       else if (ye1 >= 1.0) pos = 0;

    //       ye1 = myservo.write(servoPin[digit], pos, speed, ke);
    //       vTaskDelay(2000);
    //     }
    //     if (ye1 <= 0.0 ) pos = 90;
    //     else if (ye1 >= 1.0) pos = 0;

    //     ye1 = myservo.write(servoPin[11], pos, speed, ke);

    //     temp_token_str = token_str;
    //     temp_token = token;
    //   }
    // }
    vTaskDelay(4000);
  }
}