#include "SingleVNH5019MotorShield.h"
const int left_ina = 2;
const int left_en = 3;
const int left_pwm = 5;
const int left_cs = A7;
const int left_inb = 4;

const int right_ina = 8;
const int right_en = 6;
const int right_pwm = 9;
const int right_cs = A0;
const int right_inb = 7;

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

void setup()
{
  Serial.begin(9600);
  Serial.println("Single VNH5019 Motor Shield");
  //md.init();
  left_motor.init();
  right_motor.init();
}

void loop()
{
  if (Serial.available() > 0){
    int left = Serial.parseInt();
    int right =Serial.parseInt();
    if (Serial.read() == '\n'){
      Serial.print("left: ");
      Serial.println(left);
      Serial.print("right: ");
      Serial.println(right);
      left_motor.setM1Speed(left);
      right_motor.setM1Speed(right);
    }
    /*
    int inByte=Serial.read();
    switch(inByte){
      case 'w':
        Serial.write("w");
        left_motor.setM1Speed(100);
        right_motor.setM1Speed(100);
        break;
      case 's':
        Serial.write("s");
        left_motor.setM1Speed(-100);
        right_motor.setM1Speed(-100);
        break;
      case '\n':
        break;
      default:
        left_motor.setM1Speed(0);
        right_motor.setM1Speed(0);
        Serial.write("else");
        
        break;
    } 
    */
  }
}
