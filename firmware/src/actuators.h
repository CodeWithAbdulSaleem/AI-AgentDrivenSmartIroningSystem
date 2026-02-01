#ifndef ACTUATORS_H
#define ACTUATORS_H

#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

class ActuatorManager {
private:
    uint8_t relayPin;
    uint8_t buzzerPin;
    uint8_t ledPin;
    LiquidCrystal_I2C* lcd;

public:
    ActuatorManager(uint8_t relay_pin, uint8_t buzzer_pin, uint8_t led_pin);
    void begin();
    void setRelay(bool state);
    void setBuzzer(bool state);
    void setLed(bool state);
    void showStatus(String line1, String line2);
    void showData(float temp, float humidity, bool fabricDetected, bool wifiStatus);
    void clearLcd();
};

#endif
