#include "connectivity.h"

ConnectivityManager::ConnectivityManager() : client(wifiClient) {
    lastReconnectAttempt = 0;
}

void ConnectivityManager::begin() {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    client.setServer(TB_SERVER, 1883);
}

void ConnectivityManager::loop() {
    if (!client.connected()) {
        long now = millis();
        if (now - lastReconnectAttempt > 5000) {
            lastReconnectAttempt = now;
            // Attempt to reconnect
            if (isWifiConnected()) { // Only try MQTT if WiFi is up
                reconnect();
            }
        }
    } else {
        client.loop();
    }
}

bool ConnectivityManager::isWifiConnected() {
    return WiFi.status() == WL_CONNECTED;
}

bool ConnectivityManager::isConnected() {
    return client.connected();
}

void ConnectivityManager::reconnect() {
    // Loop until we're reconnected (Removed blocking loop for non-blocking behavior in main)
    if (!client.connected()) {
        if (client.connect("ESP32_SmartIron", TB_TOKEN, NULL)) {
            // Subscriptions or other init actions if needed
            client.subscribe("v1/devices/me/rpc/request/+"); // Example subscribe
        }
    }
}

void ConnectivityManager::sendTelemetry(float temperature, float humidity, bool fabricDetected, String fabricType, String status) {
    if (!client.connected()) return;

    String payload = "{";
    payload += "\"temperature\":" + String(temperature) + ",";
    payload += "\"humidity\":" + String(humidity) + ",";
    payload += "\"fabric_detected\":" + String(fabricDetected ? "true" : "false") + ",";
    payload += "\"fabric_type\":\"" + fabricType + "\",";
    payload += "\"status\":\"" + status + "\"";
    payload += "}";

    client.publish("v1/devices/me/telemetry", payload.c_str());
}

void ConnectivityManager::setCallback(MQTT_CALLBACK_SIGNATURE) {
    client.setCallback(callback);
}
