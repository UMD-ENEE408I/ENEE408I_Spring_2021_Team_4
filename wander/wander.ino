#include "SingleVNH5019MotorShield.h"
//use ratio code to find speeds
const int left_speed1=100;
const int right_speed1=170;
const int left_speed2=200;
const int right_speed2=295;
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
const float threshDist = 50;
float distL, distM, distR;
//returns ping distance in cm
float getPing(int echoPin, int trigPin){
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(pulseLen);
    digitalWrite(trigPin, LOW);
    return 0.017 * pulseIn(echoPin, (HIGH)); // read high pulse length
    // round trip time * 0.034cm/microsec / 2
}

SingleVNH5019MotorShield left_motor=SingleVNH5019MotorShield(left_ina, left_inb, left_pwm, left_en, left_cs);
SingleVNH5019MotorShield right_motor=SingleVNH5019MotorShield(right_ina, right_inb, right_pwm, right_en, right_cs);
void stopIfFault()
{
  if (left_motor.getM1Fault())
  {
    Serial.println("Left motor fault");
    while(1);
  }
  if (right_motor.getM1Fault())
  {
    Serial.println("Right motor fault");
    while(1);
  }
}
void setup() {
  // put your setup code here, to run once:
    pinMode(echoL, INPUT);
    pinMode(echoM, INPUT);
    pinMode(echoR, INPUT);
    pinMode(trigL, OUTPUT);
    pinMode(trigM, OUTPUT);
    pinMode(trigR, OUTPUT);
    Serial.begin(9600);
    left_motor.init();
    right_motor.init();

}

void loop() {
  // put your main code here, to run repeatedly:
  distL = getPing(echoL, trigL);
  distM = getPing(echoM, trigM);
  distR = getPing(echoR, trigR);
  Serial.print("left:");
  Serial.print(distL);
  Serial.print(" mid:");
  Serial.print(distM);
  Serial.print(" right:");
  Serial.println(distR);

  if (distM > threshDist && distL > threshDist && distR > threshDist){
    left_motor.setM1Speed(left_speed1);
    right_motor.setM1Speed(right_speed1);
  }
  else{
    if(distL > distR){
      left_motor.setM1Speed(-left_speed1);
      right_motor.setM1Speed(right_speed1);
    }
    else{
      right_motor.setM1Speed(-right_speed1);
      left_motor.setM1Speed(left_speed1);
    }
    
  }

}
