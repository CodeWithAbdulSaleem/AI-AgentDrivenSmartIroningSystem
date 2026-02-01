#ifndef OFFLINE_AI_H
#define OFFLINE_AI_H

#include "config.h"
#include <Arduino.h>

struct Decision {
    bool relayState;
    bool buzzerState;
    bool ledState;
    String statusMessage;
};

class OfflineDecisionEngine {
private:
    float safeTempThreshold;

public:
    OfflineDecisionEngine();
    Decision decide(float temp, float humidity, bool fabricDetected);
};

#endif
