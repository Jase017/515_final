#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>

#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

const char* ssid = "UW MPSK";
const char* password = "$yUAs?3tCd"; // Replace with your network password
#define DATABASE_URL "https://pawsitude-2bab7-default-rtdb.firebaseio.com/" // Replace with your database URL
#define API_KEY "AIzaSyCc5UcrsiyYfwE2gnfK_yHRYg1dtl7cFf8" // Replace with your API key
#define MAX_WIFI_RETRIES 5 // Maximum number of WiFi connection retries

// Define Firebase Data object
FirebaseData fbdo;

FirebaseAuth auth;
FirebaseConfig config;

unsigned long lastMeasurementTime = 0;
int count = 0;
bool signupOK = false;

// Sound Sensor Pin
const int sensorPin = A10;
const int soundThreshold = 150; // Sound threshold

// Function prototypes
void connectToWiFi();
void initFirebase();
void sendDataToFirebase(int count);

void setup() {
  Serial.begin(115200);
  pinMode(sensorPin, INPUT);

  connectToWiFi();
  initFirebase();
}

void loop() {
  // Read sound level
  int soundLevel = analogRead(sensorPin);
  Serial.print("Sound Level: ");
  Serial.println(soundLevel);

  // Debouncing mechanism
  if (soundLevel > soundThreshold && millis() - lastMeasurementTime > 200) {
    count++;
    lastMeasurementTime = millis();
    Serial.println("Barking detected! Uploading data to Firebase...");
    sendDataToFirebase(count); // Send data to Firebase when barking is detected
  }

  delay(100); // Delay to stabilize readings
}

void connectToWiFi()
{
  Serial.println(WiFi.macAddress());
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi");
  int wifiCnt = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
    wifiCnt++;
    if (wifiCnt > MAX_WIFI_RETRIES){
      Serial.println("WiFi connection failed");
      ESP.restart();
    }
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void initFirebase()
{
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;

  if (Firebase.signUp(&config, &auth, "", "")){
    Serial.println("Firebase signup OK");
    signupOK = true;
  }
  else{
    Serial.printf("Firebase signup failed: %s\n", config.signer.signupError.message.c_str());
  }
  
  config.token_status_callback = tokenStatusCallback; // See addons/TokenHelper.h
  Firebase.begin(&config, &auth);
  Firebase.reconnectNetwork(true);
}

void sendDataToFirebase(int countValue) {
  if (Firebase.ready() && signupOK) {
    if (Firebase.RTDB.setInt(&fbdo, "Barking/count", countValue)){
      Serial.println("Firebase upload SUCCESS");
      Serial.print("PATH: ");
      Serial.println(fbdo.dataPath());
      Serial.print("TYPE: ");
      Serial.println(fbdo.dataType());
    } else {
      Serial.println("Firebase upload FAILED");
      Serial.print("REASON: ");
      Serial.println(fbdo.errorReason());
    }
  }
}
