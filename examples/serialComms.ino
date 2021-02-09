// Demonstrates basic serial communication between the Arduino and Xavier

void setup()
{
  Serial.begin(9600);
}

void loop()
{
  if (Serial.available())
  {
    int recv = Serial.read(); // read single byte
    Serial.print("Hello Jetson! I received: ");
    Serial.println(recv, DEC);
  }
}
