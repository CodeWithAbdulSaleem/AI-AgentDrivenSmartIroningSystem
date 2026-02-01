#ifndef CONFIG_H
#define CONFIG_H

// --- WiFi Configuration ---
#define WIFI_SSID "realme"
#define WIFI_PASSWORD "12345678"

// --- ThingsBoard Configuration ---
#define TB_SERVER "demo.thingsboard.io"
#define TB_TOKEN "8PW6spbeXwZspsBTr1st"

// --- Pin Definitions ---
// Sensors
#define PIN_DHT 4   // User specified D4
#define PIN_IR 34   // User specified D34
#define PIN_SWITCH 32 // Manual mode switch

// Actuators
#define PIN_RELAY 26 // User specified D26
#define PIN_BUZZER 15 // User specified D15
#define PIN_LED 2    // User specified D2
// LCD I2C Pins: SDA=21, SCL=22 (Default ESP32 Wire pins)

// --- System Thresholds ---
#define OFFLINE_TEMP_THRESHOLD 170.0 // Celsius (Safety limit for offline mode)

#endif
