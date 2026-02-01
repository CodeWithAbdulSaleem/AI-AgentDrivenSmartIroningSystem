#ifndef CONNECTIVITY_H
#define CONNECTIVITY_H

#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"

class ConnectivityManager {
private:
    WiFiClient wifiClient;
    PubSubClient client;
    long lastReconnectAttempt;
    
    void reconnect();

public:
    ConnectivityManager();
    void begin();
    void loop();
    bool isConnected();
    bool isWifiConnected();
    void sendTelemetry(float temperature, float humidity, bool fabricDetected, String fabricType, String status);
    void setCallback(MQTT_CALLBACK_SIGNATURE);
};

#endif
