// Demonstrates ultrasonic ping sensor trio functionality

const int echoL = 2;
const int trigL = 3;
const int echoM = 4;
const int trigM = 5;
const int echoR = 6;
const int trigR = 7;
const int pulseLen = 60; // microseconds

float distL, distM, distR;

void setup() {
    pinMode(echoL, INPUT);
    pinMode(echoM, INPUT);
    pinMode(echoR, INPUT);
    pinMode(trigL, OUTPUT);
    pinMode(trigM, OUTPUT);
    pinMode(trigR, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    distL = getPing(echoL, trigL);
    distM = getPing(echoM, trigM);
    distR = getPing(echoR, trigR);
    Serial.print("left:");
    Serial.print(distL);
    Serial.print(" mid:");
    Serial.print(distM);
    Serial.print(" right:");
    Serial.println(distR);
    delay(1000);
}

// returns ping distance in cm
float getPing(int echoPin, int trigPin){
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(pulseLen);
    digitalWrite(trigPin, LOW);
    return 0.017 * pulseIn(echoPin, (HIGH)); // read high pulse length
    // round trip time * 0.034cm/microsec / 2
}
