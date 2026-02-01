#include <Arduino.h>
#include "config.h"
#include "sensors.h"
#include "actuators.h"
#include "connectivity.h"
#include "tinyml.h"
#include "blackbox.h"
#include <ArduinoJson.h>

// --- Global Objects ---
SensorManager sensors(PIN_DHT, PIN_IR);
ActuatorManager actuators(PIN_RELAY, PIN_BUZZER, PIN_LED);
ConnectivityManager connectivity;
TinyML tinyML(5);
BlackBox blackBox;

// --- State Variables ---
bool isOnline = false;
unsigned long lastTelemetryTime = 0;
const long telemetryInterval = 2000;
bool wasOnline = false;

// Global variables to store latest sensor state for training
float currentTemp = 0;
float currentHum = 0;
bool currentFabric = false;

// --- MQTT Callback ---
void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String msg;
    for (int i = 0; i < length; i++) {
        msg += (char)payload[i];
    }
    
    StaticJsonDocument<200> doc;
    deserializeJson(doc, msg);
    
    String method = doc["method"];
    if (method == "setRelay") {
        bool state = doc["params"];
        actuators.setRelay(state);
        
        tinyML.train(currentTemp, currentHum, currentFabric, state);
        blackBox.logEvent("AUTO", "Cloud setRelay " + String(state));
        
    } else if (method == "setBuzzer") {
        bool state = doc["params"];
        actuators.setBuzzer(state);
    } else if (method == "dumpLogs") {
        blackBox.dumpLogs();
    }
}

void setup() {
    Serial.begin(115200);
    
    blackBox.begin();
    sensors.begin();
    actuators.begin();
    
    connectivity.setCallback(mqttCallback);
    connectivity.begin();
    
    delay(1000);
}

void loop() {
    // 1. Connectivity Check
    connectivity.loop();
    bool wifiUp = connectivity.isWifiConnected();
    bool mqttUp = connectivity.isConnected();
    isOnline = wifiUp && mqttUp;

    // Log Network Transitions
    if (isOnline && !wasOnline) {
        blackBox.logEvent("NET", "Online Mode Active");
        wasOnline = true;
    } else if (!isOnline && wasOnline) {
        blackBox.logEvent("NET", "Connection Lost - Offline Mode");
        wasOnline = false;
    }

    // 2. Read Sensors
    currentTemp = sensors.getTemperature();
    currentHum = sensors.getHumidity();
    currentFabric = sensors.isFabricDetected();
    String currentFabricType = sensors.getFabricType();
    
    // Check Serial for manual Dump command
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        if (cmd == "dumpLogs") {
            blackBox.dumpLogs();
        } else if (cmd == "clearLogs") {
             blackBox.clearLogs();
        }
    }

    // 3. Control Logic
    if (isOnline) {
        // --- ONLINE MODE ---
        unsigned long now = millis();
        if (now - lastTelemetryTime > telemetryInterval) {
            lastTelemetryTime = now;
            connectivity.sendTelemetry(currentTemp, currentHum, currentFabric, currentFabricType, "Online (Learning)");
        }
        
        // Safety Override
        if (currentTemp > OFFLINE_TEMP_THRESHOLD) {
             actuators.setRelay(false);
             actuators.setBuzzer(true);
             blackBox.logEvent("ALRT", "Overheat Safety Trip (Online) " + String(currentTemp));
        }

        actuators.showData(currentTemp, currentHum, currentFabric, true);
        
    } else {
        // --- OFFLINE MODE (ADAPTIVE AI) ---
        bool predictedRelayState = tinyML.predict(currentTemp, currentHum, currentFabric);
        int samples = tinyML.getSampleCount();
        
        String statusMsg = "AI (Sim): ";
        if (samples < 1) statusMsg = "No Training"; 
        
        if (samples > 0) {
            actuators.setRelay(predictedRelayState);
            statusMsg += predictedRelayState ? "ON" : "OFF";
        } else {
            actuators.setRelay(false); 
        }
        
        actuators.setBuzzer(false); 
        
        // Safety Check
        if (currentTemp > OFFLINE_TEMP_THRESHOLD) {
             actuators.setRelay(false);
             actuators.setBuzzer(true);
             statusMsg = "Overheat!";
             blackBox.logEvent("ALRT", "Overheat Safety Trip (Offline) " + String(currentTemp));
        }

        actuators.showStatus("OFFLINE AI L:" + String(samples), statusMsg);
    }
}
