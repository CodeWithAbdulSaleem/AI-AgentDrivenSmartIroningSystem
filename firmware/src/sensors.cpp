#include "sensors.h"

SensorManager::SensorManager(uint8_t dht_pin, uint8_t ir_pin) {
    dhtPin = dht_pin;
    irPin = ir_pin;
    dht = new DHT(dhtPin, DHT11);
}

void SensorManager::begin() {
    pinMode(irPin, INPUT);
    dht->begin();
}

float SensorManager::getTemperature() {
    float t = dht->readTemperature();
    if (isnan(t)) return -1.0;
    return t;
}

float SensorManager::getHumidity() {
    float h = dht->readHumidity();
    if (isnan(h)) return -1.0;
    return h;
}

bool SensorManager::isFabricDetected() {
    // Robust detection: Analog value drops when object reflects IR
    // Threshold ~3500 (Adjust based on potentiometer/ambient light)
    return analogRead(irPin) < 3500; 
}

String SensorManager::getFabricType() {
    int sensorValue = analogRead(irPin);
    
    // Simple Reflection-based Classification Logic
    // White/Smooth (Cotton/Silk) -> High Reflection -> Low Analog Value
    // Dark/Rough (Wool/Denim) -> Low Reflection -> High Analog Value
    
    if (sensorValue > 3500) return "Unknown"; // No fabric
    if (sensorValue < 1000) return "Cotton"; // High Reflectivity
    if (sensorValue < 1800) return "Nylon";
    if (sensorValue < 2500) return "Silk";
    if (sensorValue < 3500) return "Wool"; // Low Reflectivity
    
    return "Unknown";
}
