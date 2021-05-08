#include "SingleVNH5019MotorShield.h"

const int leftSpd = -120;
const int rightSpd = 160;

const int delay_len = 800; // ms

//left motor
const int left_ina = 2;
const int left_en = 3;
const int left_pwm = 5;
const int left_cs = A7;
const int left_inb = 4;

//right motor
const int right_ina = 8;
const int right_en = 6;
const int right_pwm = 9;
const int right_cs = A0;
const int right_inb = 7;

//ping sensor pins
const int echoL = 18; //A4
const int trigL = 19; //A5
const int echoM = 11;
const int trigM = 10;
const int echoR = 16; //A2
const int trigR = 17; //A3
const int pulseLen = 60;

// globals
float distL, distM, distR;
int command;

//returns ping distance in cm
float getPing(int echoPin, int trigPin){
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(pulseLen);
    digitalWrite(trigPin, LOW);
    return 0.017 * pulseIn(echoPin, (HIGH)); // read high pulse length
    // round trip time * 0.034cm/microsec / 2
}

void updateSensors() {
    distL = getPing(echoL, trigL);
    distM = getPing(echoM, trigM);
    distR = getPing(echoR, trigR);
}

SingleVNH5019MotorShield left_motor=SingleVNH5019MotorShield(left_ina, left_inb, left_pwm, left_en, left_cs);
SingleVNH5019MotorShield right_motor=SingleVNH5019MotorShield(right_ina, right_inb, right_pwm, right_en, right_cs);

void stopIfFault() {
    if (left_motor.getM1Fault()) {
        Serial.println("Left motor fault");
        while(1);
    }
    if (right_motor.getM1Fault()) {
        Serial.println("Right motor fault");
        while(1);
    }
}

void forward() {
    left_motor.setM1Speed(leftSpd);
    right_motor.setM1Speed(rightSpd);
}

void backward() {
    left_motor.setM1Speed(-leftSpd);
    right_motor.setM1Speed(-rightSpd);
}

void left() {
    left_motor.setM1Speed(-leftSpd);
    right_motor.setM1Speed(rightSpd);
}

void right() {
    left_motor.setM1Speed(leftSpd);
    right_motor.setM1Speed(-rightSpd);
}

void leftTurn() {
    left_motor.setM1Speed(-leftSpd);
    right_motor.setM1Speed(rightSpd);
    delay(delay_len);
    stopAll();
}

void rightTurn() {
    left_motor.setM1Speed(leftSpd);
    right_motor.setM1Speed(-rightSpd);
    delay(delay_len);
    stopAll();
}

void stopAll() {
    left_motor.setM1Speed(0);
    right_motor.setM1Speed(0);
}

void wander() {
    while(!Serial.available()) {
        updateSensors();
        if (distM > 30.0 && distL > 20.0 && distR > 20.0){
            forward();
        } else {
            if(distL > distR){ // turn left
                leftTurn();
                delay(delay_len);
                stopAll();
            } else { // turn right
                rightTurn();
                delay(delay_len);
                stopAll();
            }
        }
    }
}

void setup() {
    pinMode(echoL, INPUT);
    pinMode(echoM, INPUT);
    pinMode(echoR, INPUT);
    pinMode(trigL, OUTPUT);
    pinMode(trigM, OUTPUT);
    pinMode(trigR, OUTPUT);
    Serial.begin(9600);
    left_motor.init();
    right_motor.init();
    command = 's'; // default stop
}

void loop() {
    void updateSensors();    

    if (Serial.available()) {
        command = Serial.read();
        //Serial.print("Hello Jetson! I received: ");
        Serial.println(command, DEC);
    }
    switch(command) {
        case 'w':
            //Serial.println("WANDER");
            wander();
            break;
        case 'f':
            forward();
            break;
        case 'b':
            backward();
            break;
        case 'l':
            left();
            break;
        case 'r':
            right();
            break;
        case 's':
            stopAll();
            break;
        default:
            break;
    }
}
