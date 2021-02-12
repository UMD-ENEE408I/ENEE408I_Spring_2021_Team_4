#include "SingleVNH5019MotorShield.h"
/*
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
*/
const int ina = 2;
const int en = 3;
const int pwm = 5;
const int cs = A7;
const int inb = 4;

SingleVNH5019MotorShield md=SingleVNH5019MotorShield(ina, inb, pwm, en, cs);;

void stopIfFault()
{
  if (md.getM1Fault())
  {
    Serial.println("M1 fault");
    while(1);
  }
}

void setup()
{
  Serial.begin(115200);
  Serial.println("Single VNH5019 Motor Shield");
  md.init();
}

void loop()
{
  for (int i = 0; i <= 400; i++)
  {
    md.setM1Speed(i);
    stopIfFault();
    if (i%200 == 100)
    {
      Serial.print("M1 current: ");
      Serial.println(md.getM1CurrentMilliamps());
    }
    delay(2);
  }
  
  for (int i = 400; i >= -400; i--)
  {
    md.setM1Speed(i);
    stopIfFault();
    if (i%200 == 100)
    {
      Serial.print("M1 current: ");
      Serial.println(md.getM1CurrentMilliamps());
    }
    delay(2);
  }
  
  for (int i = -400; i <= 0; i++)
  {
    md.setM1Speed(i);
    stopIfFault();
    if (i%200 == 100)
    {
      Serial.print("M1 current: ");
      Serial.println(md.getM1CurrentMilliamps());
    }
    delay(2);
  }
}
