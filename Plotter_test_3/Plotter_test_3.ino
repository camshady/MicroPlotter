
#include <Servo.h>

Servo S_servo;
Servo E_servo;// create servo object to control a servo
// twelve servo objects can be created on most boards

int S_current = 123;
int E_current = 0;


void setup() {
  S_servo.attach(6);  // attaches the servo on pin 9 to the servo object
  E_servo.attach(5);
  Serial.begin(115200);

  S_servo.write(S_current);
  E_servo.write(E_current);
}

void loop() {
    if(Serial.available() > 0) {
      int angle = Serial.read();
      Serial.println(S_current);
      int S_target = angle;      
      S_move(S_current, S_target);
      //move_servo(current, target, 1);
      

      
  }
}

void S_move(int current, int target) {

  while (current < target) {
    current = current + 1; // increments of 1 degree
    S_servo.write(current);
    delay(5); // wait 15ms between movements.
  }   
  while (current > target) {
    current = current - 1; // increments of 1 degree
    S_servo.write(current);
    delay(5); // wait 15ms between movements.
  }   

  S_current = current;
}
