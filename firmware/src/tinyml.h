#ifndef TINYML_H
#define TINYML_H

#include <Arduino.h>

struct DataPoint {
    float temp;
    float humidity;
    bool fabricDetected;
    bool relayState;
    bool isValid;
};

class TinyML {
private:
    static const int MAX_SAMPLES = 20;
    DataPoint memory[MAX_SAMPLES];
    int head;
    int k; // k-neighbors

public:
    TinyML(int k_neighbors = 3);
    void train(float temp, float hum, bool fabric, bool relayState);
    bool predict(float temp, float hum, bool fabric);
    int getSampleCount();
};

#endif
