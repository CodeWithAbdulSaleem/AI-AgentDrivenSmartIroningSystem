#include "offline_ai.h"

OfflineDecisionEngine::OfflineDecisionEngine() {
    safeTempThreshold = OFFLINE_TEMP_THRESHOLD;
}

Decision OfflineDecisionEngine::decide(float temp, float humidity, bool fabricDetected) {
    Decision d;
    
    // Default Safe State
    d.relayState = false;
    d.buzzerState = false;
    d.ledState = false; // Led could indicate heating
    d.statusMessage = "Idle";

    if (!fabricDetected) {
        d.relayState = false;
        d.statusMessage = "No Fabric";
        // Safety: If temp is very high even without fabric, maybe alert?
        if (temp > safeTempThreshold) {
             d.buzzerState = true;
             d.statusMessage = "Cooldown req!";
        }
    } else {
        // Fabric Detected
        if (temp < safeTempThreshold) {
            d.relayState = true;
            d.ledState = true;
            d.statusMessage = "Heating (Safe)";
        } else {
            d.relayState = false;
            d.buzzerState = true; // Alert Overheat
            d.ledState = false;
            d.statusMessage = "Overheat Alert!";
        }
    }

    return d;
}
