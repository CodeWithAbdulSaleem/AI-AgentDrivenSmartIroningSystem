#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>
#include <DHT.h>

class SensorManager {
private:
    uint8_t dhtPin;
    uint8_t irPin;
    DHT* dht;

public:
    SensorManager(uint8_t dht_pin, uint8_t ir_pin);
    void begin();
    float getTemperature();
    float getHumidity();
    bool isFabricDetected(); // Based on IR sensor
    String getFabricType();
};

#endif
