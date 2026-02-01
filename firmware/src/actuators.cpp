#include "actuators.h"

ActuatorManager::ActuatorManager(uint8_t relay_pin, uint8_t buzzer_pin, uint8_t led_pin) {
    relayPin = relay_pin;
    buzzerPin = buzzer_pin;
    ledPin = led_pin;
    // Address 0x27 is common for 16x2 I2C LCDs. 
    lcd = new LiquidCrystal_I2C(0x27, 16, 2); 
}

void ActuatorManager::begin() {
    pinMode(relayPin, OUTPUT);
    pinMode(buzzerPin, OUTPUT);
    pinMode(ledPin, OUTPUT);
    
    // Initial States
    digitalWrite(relayPin, LOW); // Assume HIGH trigger is ON (Check relay module)
    digitalWrite(buzzerPin, LOW);
    digitalWrite(ledPin, LOW);

    lcd->init();
    lcd->backlight();
    showStatus("System Init...", "Pls Wait");
}

void ActuatorManager::setRelay(bool state) {
    digitalWrite(relayPin, state ? HIGH : LOW);
}

void ActuatorManager::setBuzzer(bool state) {
    digitalWrite(buzzerPin, state ? HIGH : LOW);
}

void ActuatorManager::setLed(bool state) {
    digitalWrite(ledPin, state ? HIGH : LOW);
}

void ActuatorManager::showStatus(String line1, String line2) {
    lcd->clear();
    lcd->setCursor(0, 0);
    lcd->print(line1);
    lcd->setCursor(0, 1);
    lcd->print(line2);
}

void ActuatorManager::showData(float temp, float humidity, bool fabricDetected, bool wifiStatus) {
    lcd->setCursor(0, 0);
    lcd->print("T:"); 
    lcd->print(temp, 1);
    lcd->print("C ");
    lcd->print(wifiStatus ? "ON" : "OFF");
    
    lcd->setCursor(0, 1);
    if (fabricDetected) {
        lcd->print("Fab:YES H:");
        lcd->print(humidity, 0);
        lcd->print("%");
    } else {
        lcd->print("No Fabric     ");
    }
}

void ActuatorManager::clearLcd() {
    lcd->clear();
}
