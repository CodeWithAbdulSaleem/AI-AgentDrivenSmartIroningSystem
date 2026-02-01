#include "tinyml.h"

TinyML::TinyML(int k_neighbors) {
    head = 0;
    k = k_neighbors;
    // Init invalid memory
    for (int i = 0; i < MAX_SAMPLES; i++) {
        memory[i].isValid = false;
    }
}

void TinyML::train(float temp, float hum, bool fabric, bool relayState) {
    // Basic circular buffer
    memory[head].temp = temp;
    memory[head].humidity = hum;
    memory[head].fabricDetected = fabric;
    memory[head].relayState = relayState;
    memory[head].isValid = true;
    
    head = (head + 1) % MAX_SAMPLES;
}

bool TinyML::predict(float temp, float hum, bool fabric) {
    int validCount = 0;
    struct Neighbor {
        int index;
        float distance;
    };
    Neighbor neighbors[MAX_SAMPLES];
    
    for (int i = 0; i < MAX_SAMPLES; i++) {
        if (!memory[i].isValid) continue;
        
        if (memory[i].fabricDetected != fabric) {
            neighbors[validCount] = {i, 99999.0}; 
        } else {
            float diffT = abs(memory[i].temp - temp);
            float diffH = abs(memory[i].humidity - hum);
            neighbors[validCount] = {i, diffT + (0.5 * diffH)};
        }
        validCount++;
    }

    if (validCount == 0) return false;

    for (int i = 0; i < validCount - 1; i++) {
        for (int j = 0; j < validCount - i - 1; j++) {
            if (neighbors[j].distance > neighbors[j+1].distance) {
                Neighbor tempN = neighbors[j];
                neighbors[j] = neighbors[j+1];
                neighbors[j+1] = tempN;
            }
        }
    }

    int votesOn = 0;
    int k_eff = (validCount < k) ? validCount : k;
    
    for (int i = 0; i < k_eff; i++) {
        int idx = neighbors[i].index;
        if (neighbors[i].distance > 5000) continue; 
        
        if (memory[idx].relayState) {
            votesOn++;
        }
    }
    
    return (votesOn > k_eff / 2);
}

int TinyML::getSampleCount() {
    int c = 0;
    for(int i=0; i<MAX_SAMPLES; i++) if(memory[i].isValid) c++;
    return c;
}
