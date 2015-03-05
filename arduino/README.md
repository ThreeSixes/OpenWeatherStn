This folder contains a number of Arduino sketches for both sensors and PoCs. Copy or symlnink this folder to your Arduino sketch folder to use the desired sketches!

===========================
Arduino sensor module code:
===========================

compoundSensor: Arduino code to read anemometer (supports average wind speed over sample period and max to detect gusts), rainfall severity sensor, and ambient light level. This sensor is designed to be accessed via I2C, and there is a Python class to support reading data from this sensor and a test script in https://github.com/ThreeSixes/OpenWeatherStn/tree/master/rpi. It also utilizes Timer1, an Arduino library that leverages the ATMEGA's built-in timers to control the sampling period. See http://playground.arduino.cc/Code/Timer1 for more details. 

==================
PoC and test code:
==================

magWindVeinTest: A quick test of the HMC5883L-based weather vein sensor. This function will be migrated to the RPi since the HMC5883L supports I2C.

