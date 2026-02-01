#ifndef BLACKBOX_H
#define BLACKBOX_H

#include <Arduino.h>
#include <SPIFFS.h>

class BlackBox {
private:
    const char* logFile = "/system.log";
    bool fileSystemMounted;

public:
    BlackBox();
    void begin();
    void logEvent(String type, String message);
    void dumpLogs();
    void clearLogs();
};

#endif
