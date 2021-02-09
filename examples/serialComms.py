import serial
import time

arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1) # port, baudrate, timeout

print("begin serial communication")

while True:
    arduino.write(b'a')
    try:
        data = arduino.readline()
        if data:
            print('Incoming from Arduino: ' +data.decode('UTF-8').rstrip('\n'));
        time.sleep(2)
    except:
        arduino.close()
