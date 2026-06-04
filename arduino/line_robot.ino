#include <SoftwareSerial.h>
#include "config.h"

// Line robot: autonomous follower with remote LEFT/RIGHT/STOP branch control.
SoftwareSerial bt(10, 11); // RX, TX for HC-05

int lastError = 0;
float integral = 0;
float derivativeFilter = 0;
int lastTurnDirection = 1;

int currentLeftSpeed = 0;
int currentRightSpeed = 0;

int baseSpeed = 145;
int maxSpeed = 255;
int rampStep = 22;

float Kp = 0.7;
float Ki = 0.0;
float Kd = 0.38;

int targetBranch = 0; // -1 left, +1 right, 0 autonomous
bool remoteActive = false;
bool branchBiasActive = false;
bool awaitingStopAck = false;

void motor_c(char motor_n, char direction_m, int speed_m) {
  if (invertMotorDirection) direction_m = !direction_m;
  if (motor_n == 1) {
    if (direction_m == 1) {
      digitalWrite(4, HIGH);
      analogWrite(5, speed_m);
    } else {
      digitalWrite(4, LOW);
      analogWrite(5, speed_m);
    }
  } else {
    if (direction_m == 1) {
      digitalWrite(7, HIGH);
      analogWrite(6, speed_m);
    } else {
      digitalWrite(7, LOW);
      analogWrite(6, speed_m);
    }
  }
}

void setMotor(char motor_n, int speed) {
  char dir = 0;
  if (speed < 0) { dir = 1; speed = -speed; }
  if (speed > 255) speed = 255;
  motor_c(motor_n, dir, speed);
}

int rampToward(int currentValue, int targetValue, int stepSize) {
  if (currentValue < targetValue) {
    currentValue += stepSize;
    if (currentValue > targetValue) currentValue = targetValue;
  } else if (currentValue > targetValue) {
    currentValue -= stepSize;
    if (currentValue < targetValue) currentValue = targetValue;
  }
  return currentValue;
}

void readSensors(int vals[5]) {
  for (int i = 0; i < 5; ++i) {
    int v = digitalRead(sensorPins[i]);
    vals[i] = (v == LOW) ? 1 : 0; // assume active low sensors
  }
}

int computeError(const int vals[5], int &activeCount) {
  activeCount = 0;
  int weighted = 0;
  for (int i = 0; i < 5; ++i) {
    if (vals[i]) { activeCount++; weighted += weightsArr[i]; }
  }
  if (activeCount == 0) return lastTurnDirection * 220;
  return weighted / activeCount;
}

bool forkDetected(const int vals[5]) {
  // outside left and right sensors both detect line
  return (vals[0] && vals[4]);
}

bool stopMarkerDetected(const int vals[5]) {
  // all 5 sensors detect (stop marker)
  for (int i = 0; i < 5; ++i) if (!vals[i]) return false;
  return true;
}

void processBT() {
  static String buf;
  while (bt.available()) {
    char c = bt.read();
    if (c == '\n' || c == '\r') continue;
    buf += c;
  }
  if (buf.length()) {
    Serial.print("BT msg: "); Serial.println(buf);
    if (buf.startsWith("TO;LINE;CMD;")) {
      String cmd = buf.substring(strlen("TO;LINE;CMD;"));
      cmd.trim();
      if (cmd == "LEFT") { targetBranch = -1; remoteActive = true; bt.println("ACK;FROM;LINE;STATE;RECEIVED"); }
      else if (cmd == "RIGHT") { targetBranch = 1; remoteActive = true; bt.println("ACK;FROM;LINE;STATE;RECEIVED"); }
      else if (cmd == "STOP") { remoteActive = false; targetBranch = 0; bt.println("ACK;FROM;LINE;STATE;STOPPED"); }
      else { bt.println("ACK;FROM;LINE;STATE;UNKNOWN_CMD"); }
    }
    buf = "";
  }
}

void setup() {
  // motor pins
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  for (int i = 0; i < 5; ++i) pinMode(sensorPins[i], INPUT);

  Serial.begin(115200);
  bt.begin(38400);
  Serial.println("Line robot starting");
}

void loop() {
  processBT();

  int s[5];
  readSensors(s);
  if (remoteActive && targetBranch != 0) {
    // wait until fork detected; when fork found, enter branch bias mode
    if (!branchBiasActive) {
      if (forkDetected(s)) {
        branchBiasActive = true;
      }
    }

    if (branchBiasActive) {
      // at fork: bias toward chosen branch until center sensor reacquires new line
      if (targetBranch == -1) {
        currentLeftSpeed = rampToward(currentLeftSpeed, baseSpeed - 40, rampStep);
        currentRightSpeed = rampToward(currentRightSpeed, baseSpeed + 40, rampStep);
      } else {
        currentLeftSpeed = rampToward(currentLeftSpeed, baseSpeed + 40, rampStep);
        currentRightSpeed = rampToward(currentRightSpeed, baseSpeed - 40, rampStep);
      }
      setMotor(0, currentLeftSpeed);
      setMotor(1, currentRightSpeed);

      // re-read sensors to check for stop marker or center reacquire
      readSensors(s);
      if (stopMarkerDetected(s)) {
        // reached final stop: stop and ack
        currentLeftSpeed = rampToward(currentLeftSpeed, 0, rampStep);
        currentRightSpeed = rampToward(currentRightSpeed, 0, rampStep);
        setMotor(0, currentLeftSpeed);
        setMotor(1, currentRightSpeed);
        bt.println("ACK;FROM;LINE;STATE;DONE");
        remoteActive = false;
        targetBranch = 0;
        branchBiasActive = false;
        awaitingStopAck = false;
        delay(500);
      } else if (s[2]) {
        // center sensor sees the new line — resume normal following
        branchBiasActive = false;
        // mark that we should still wait for the stop marker later
        awaitingStopAck = true;
        // clear targetBranch so we don't re-enter fork wait
        targetBranch = 0;
        // fall through to normal PID on next loop
      }

      delay(10);
      // while branchBiasActive we handled motion, so skip PID for this iteration
      if (branchBiasActive) return;
    }
  }

  // Otherwise run simple line following PID loop (lightweight)
  int activeCount = 0;
  int error = computeError(s, activeCount);
  if (error > 0) lastTurnDirection = 1; else if (error < 0) lastTurnDirection = -1;

  float derivative = error - lastError;
  derivativeFilter = derivativeFilter * 0.6 + derivative * 0.4;
  integral += error;
  if (integral > 2500.0) integral = 2500.0;
  if (integral < -2500.0) integral = -2500.0;

  float correction = (Kp * error) + (Kd * derivativeFilter) + (Ki * integral);

  int targetBaseSpeed = baseSpeed;
  int targetLeftSpeed = targetBaseSpeed + (int)correction;
  int targetRightSpeed = targetBaseSpeed - (int)correction;

  targetLeftSpeed = constrain(targetLeftSpeed, 0, maxSpeed);
  targetRightSpeed = constrain(targetRightSpeed, 0, maxSpeed);

  currentLeftSpeed = rampToward(currentLeftSpeed, targetLeftSpeed, rampStep);
  currentRightSpeed = rampToward(currentRightSpeed, targetRightSpeed, rampStep);

  setMotor(0, currentLeftSpeed);
  setMotor(1, currentRightSpeed);

  // If we're awaiting final stop acknowledgement, check for the stop marker here
  if (awaitingStopAck && stopMarkerDetected(s)) {
    // stop and ack
    currentLeftSpeed = rampToward(currentLeftSpeed, 0, rampStep);
    currentRightSpeed = rampToward(currentRightSpeed, 0, rampStep);
    setMotor(0, currentLeftSpeed);
    setMotor(1, currentRightSpeed);
    bt.println("ACK;FROM;LINE;STATE;DONE");
    remoteActive = false;
    awaitingStopAck = false;
    delay(500);
  }
  lastError = error;
  delay(5);
}
