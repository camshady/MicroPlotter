# https://www.instructables.com/Arduino-Python-Communication-via-USB/

#Communicates from python to arduino
import serial, time
arduino = serial.Serial('COM5', 115200, timeout=.1)
time.sleep(1) #give the connection a second to settle
string = "Hello from Python!"
arduino.write(string.encode())
while True:
	data = (arduino.readline()).decode()
	if data:
		print(data.rstrip('\n')) #strip out the new lines for now
		# (better to do .read() in the long run for this reason