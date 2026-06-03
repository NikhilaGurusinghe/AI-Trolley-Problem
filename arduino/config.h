// Pin mapping for the line robot.
#ifndef CONFIG_H
#define CONFIG_H

// Sensor pins are kept away from the motor and Bluetooth pins.
const int sensorPins[5] = {2, 3, 8, 9, 12};
const int weightsArr[5] = {-200, -100, 0, 100, 200};

const bool invertMotorDirection = true;

#endif
