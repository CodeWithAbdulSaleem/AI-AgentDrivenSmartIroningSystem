#include "blackbox.h"

BlackBox::BlackBox() {
    fileSystemMounted = false;
}

void BlackBox::begin() {
    if (!SPIFFS.begin(true)) {
        Serial.println("BLACKBOX: SPIFFS Mount Failed");
        return;
    }
    fileSystemMounted = true;
    logEvent("BOOT", "System Started");
}

void BlackBox::logEvent(String type, String message) {
    if (!fileSystemMounted) return;

    File file = SPIFFS.open(logFile, FILE_APPEND);
    if (!file) {
        Serial.println("BLACKBOX: Failed to open log file");
        return;
    }
    
    // Format: [UpsTime] TYPE: Message
    String logEntry = "[" + String(millis()/1000) + "] " + type + ": " + message + "\n";
    file.print(logEntry);
    file.close();
    
    Serial.print("LOG: ");
    Serial.print(logEntry);
}

void BlackBox::dumpLogs() {
    if (!fileSystemMounted) return;

    File file = SPIFFS.open(logFile, FILE_READ);
    if (!file) {
        Serial.println("BLACKBOX: No logs found");
        return;
    }

    Serial.println("--- BLACK BOX DUMP START ---");
    while (file.available()) {
        Serial.write(file.read());
    }
    Serial.println("--- BLACK BOX DUMP END ---");
    file.close();
}

void BlackBox::clearLogs() {
    if (!fileSystemMounted) return;
    SPIFFS.remove(logFile);
    Serial.println("BLACKBOX: Logs Cleared");
    logEvent("SYS", "Logs Cleared User Command");
}
