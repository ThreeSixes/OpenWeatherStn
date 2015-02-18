/*

Magnetometer wind vein sensor test sketch by ThreeSixes
https://github.com/ThreeSixes

This is designed to use the Parallax HMC5883L break out board in I2C mode, and 
is a proof-of-concept for the digital wind vein which will ultimately be read
by a Raspberry Pi.

*/

// Included libs.
#include <math.h> // Need this to do trig to get direction.
#include <Wire.h> // I2C support


// Configuration

// The magnetometer config variables are based on the HMC5883L datasheet
// http://www51.honeywell.com/aero/common/documents/myaerospacecatalog-documents/Defense_Brochures-documents/HMC5883L_3-Axis_Digital_Compass_IC.pdf
#define magAddr 0x1e // HMC5883 I2C address
#define magCfgBReg 0x01 // Config register B (contains sensitivity)
#define magModeReg 0x02 // Mode config register
#define magMode 0x00 // Mode value.
#define magSens 0xe0 // Magnetometer sensitivity
#define magOutReg 0x03 // First magnetometer value output register (X MSB)

#define baudRate 9600 // Serial output baud rate

#define bootDelay 100 // Start-up delay (ms)


// Setup routine.
void setup() {
  // Set up serial port
  Serial.begin(baudRate);
  
  // Start the I2C bus.  
  Wire.begin();
  
  // Wait for things to settle.
  delay(bootDelay);
  
  // Set magnetometer sensitivity to lowest vale.
  sendMag(byte(magCfgBReg), byte(magSens));
  
  // Set magnetometer mode to streaming
  sendMag(byte(magModeReg), byte(magMode));
}

// Send I2C bytes to compass
void sendMag(byte addr, byte val) {
  // Set magnetometer to streaming mode
  Wire.beginTransmission(magAddr);
  Wire.write(addr);
  Wire.write(val);
  Wire.endTransmission();
  
  return;
}

// Get x, y, and z values from magnetometer. We're using targetVar because
// returning an array is not easy to do.
void getXYZ(int targetVar[]) {
  
  // Initiate communications with compass
  Wire.beginTransmission(magAddr);
  // Ask for X, Z, and Y values, staring with X.
  Wire.write(byte(magOutReg));
  Wire.endTransmission();

  // Retrieve the data we aked for. X, Z, and Y are 2
  // bytes long so we ask for 6 bytes.
  Wire.requestFrom(magAddr, 6);
  
  // If we have 6 bytes of data coming
  if(Wire.available() <= 6) {
    
    // Set values in our target: X, Y, and Z (in that order.)
    // Since this reads bytes in return order we need to shuffle
    // the value order a bit to make it more intuitive.
    // X - Z - Y becomes X - Y - Z in our array.
    targetVar[0] = Wire.read() << 8 | Wire.read();
    targetVar[2] = Wire.read() << 8 | Wire.read();
    targetVar[1] = Wire.read() << 8 | Wire.read();
  }

  // Return.
  return;
}

// Get magnet's direction on X + Y plane relative to magnetometer
int magDir(int xScale, int yScale) {
  // Store our return value
  int retVal = 0;
  
  // Use atan2 to get direction of magnet.
  retVal = atan2(xScale, yScale) * 180 / M_PI;
  
  // Compensate for negative angle relative to zero line.
  // -90 degrees becomes 270 degrees.
  if(retVal < 0) {
    retVal = 360 - abs(retVal);
  }
  
  // Return it.
  return retVal;
}

// Main program body
void loop() {
  // Set up an array to hold our inital data.
  int currentData[] = {0, 0, 0};
  int angle = 0;
  
  // Get data from magnetometer.
  getXYZ(currentData);
  
  // Figure out where the magnet is.
  angle = magDir(currentData[0], currentData[1]);
  
  // Show the angle, X, and Y data we're getting.
  Serial.print("A = ");
  Serial.print(angle);
  Serial.print(", X = ");
  Serial.print(currentData[0]);
  Serial.print(", Y = ");
  Serial.println(currentData[1]);
  
  // Wait 1/2 a second to get new data.  
  delay(500);
}
