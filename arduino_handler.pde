int incomingByte = 0;

int RED = 13;
int GREEN = 12;

void setup() {
    Serial.begin(9600);
    pinMode(RED, OUTPUT);
    pinMode(GREEN, OUTPUT);
    digitalWrite(RED, LOW);
    digitalWrite(GREEN, LOW);
}

void loop() {
    if (Serial.available() > 0) {
        incomingByte = Serial.read();
        if (incomingByte == 'E') {
            digitalWrite(RED, HIGH);
            digitalWrite(GREEN, LOW);
        }
        else if (incomingByte == 'S') {
            digitalWrite(RED, LOW);
            digitalWrite(GREEN, HIGH);
        }
    }
}
