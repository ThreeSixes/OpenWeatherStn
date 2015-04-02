/* Compound weather data sensor by ThreeSixes
This is an Arduino project developed on an Uno to read data from
an anemometer (http://adafru.it/1733), a simple laser / CdS cell-based
rain detector, and present this data via I2C to another device.

At present this project requires the Timer1 library:
http://playground.arduino.cc/Code/Timer1

https://github.com/ThreeSixes/OpenWeatherStn
LICENSE?

== I2C register structure (i2cBuff) ==
Byte 0:  Firmware version major
Byte 1:  Firmware version minor
Byte 2:  Status register
Byte 3:  Rain sensor count MSB (Rain data is a 32 bit counter)
...
Byte 6:  Rain sensor count LSB
Byte 7:  Wind speed avg MSB
Byte 8:  Wind speed avg LSB
Byte 9:  Wind speed max MSB
Byte 10: Wind speed max LSB
Byte 11: Ambient light brightness
*/


// ************
// * Includes *
// ************

// Include I2C support for communicating with
// our data collector.
#include <Wire.h>

// Include Timer1 for hardware timer support.
#include <TimerOne.h>

// *****************
// * Configuration *
// *****************

// Installed sensors - comment out lines for sensors that aren't installed.
#define hasWind
#define hasRain
#define hasLight

// I/O config
#define rainCdS            0     // Analog pin 0 for laser light sensor
#define calDelay           100   // Rain laser detection calibration delay
#define anemometer         1     // Analog pin 1 for wind speed
#define lightCdS           2     // Analog pin 2 for ambient light sensor
#define diagLED            13    // Onboard LED for rain sensor
#define baudRate           9600  // Debug serial baud rate.

// I2C register structure
#define i2c_fwMajor        0
#define i2c_fwMinor        1
#define i2c_status         2
#define i2c_rainMSB        3
#define i2c_rain2SB        4
#define i2c_rain3SB        5
#define i2c_rainLSB        6
#define i2c_windAvgMSB     7
#define i2c_windAvgLSB     8
#define i2c_windMaxMSB     9
#define i2c_windMaxLSB     10
#define i2c_lightAvg       11

// I2C buffer config
#define i2cBuffSize        12 // Number of bytes we'll store.

// I2C status register flags
#define i2cStatus_initpoll 0x01 // We are initially polling
#define i2cStatus_data     0x02 // We have valid data in the register if this is set.
#define i2cStatus_wind     0x04 // Do we have an installed wind sensor?
#define i2cStatus_rain     0x08 // Do we have an installed rain sensor?
#define i2cStatus_light    0x10 // Do we have an installed ambient light sensor?

// Version numbers
#define versionMajor       0x00
#define versionMinor       0x04

// How long should we sample?
#define sampleTime          60  // 1 minute (60 seconds)

// I2C address info
#define myAddr             0x64

// Drop threshold config. When we're this far below the baseline we trigger
// the rain counter.
#define dropThresh         -6

// How many samples do we want per subsample?
#define subSampleSize      1000


// ***************************
// * Global vars and objects *
// ***************************

// Debug LED state
boolean ledState = LOW; // Off by default.

// Last sample data
unsigned long rainSample = 0; // Store our last complete rain sample.
unsigned int windSample = 0; // Store our last complete wind sample.
unsigned int windSampleMax = 0; // Store the max wind speed from our last complete sample.
unsigned int lightSample = 0; // Store our ambient light sample average.

// Timer
int sampleTimer = 0;

// I2C buffer and command status
uint8_t i2cBuff[i2cBuffSize]; // Store I2C registers here.
uint8_t i2cTarget = -1; // Store the command we're being sent.

// Subsampling setup
unsigned int subSampleCounter = 0; // Keep track of how many samples within a subsample we have taken.
unsigned int subSampleCount = 0; // How many subsamples have we taken?

// *************
// * Functions *
// *************

// Get incoming register ID
void receiveData(int byteCt) {
  // When the bus is clear, read a byte.
  while(Wire.available()) {
    i2cTarget = Wire.read();
  }
}

// Reutrn rain and wind data.
void sendData() {
  // Is our target command zero?
  if(i2cTarget >= 0 && i2cTarget < i2cBuffSize) {
    // Send our data buffer.
    Wire.write(i2cBuff[i2cTarget]);
  } else {
    // Send a zero?
    Wire.write(0, 1);
  }
  
  return;
}

// Set the I2C status bits in the register
void setI2CStat(uint8_t newStatus) {
  // Yup.
  i2cBuff[i2c_status] |= newStatus;
  
  return;
}

// Clear the I2C status bits in the register
void clearI2CStat(uint8_t newStatus) {
  // Yup.
  i2cBuff[i2c_status] &= ~newStatus;
  
  return;
}

// Dump I2C registers.
void dumpI2cReg() {
  //Header message
  Serial.print("I2C Buffer: ");
  
  // Print each byte
  for(int i = 0; i < i2cBuffSize; i++) {
    Serial.print("0x");
    Serial.print(i2cBuff[i], HEX);
    Serial.print(" ");
  }
  
  Serial.println();
  
  return;
}

#ifdef hasRain
  // Calibrate the CdS cell
  int calibrate() {
    // Read the CdS cell.
    int retVal = analogRead(rainCdS);

    // Send our calibrated value.
    return retVal;
  }

  // Strobe the onboard LED
  void strobe() {
    // Invert the LED state.
    if(ledState == HIGH) {
      ledState = LOW;
    } else {
      ledState = HIGH;
    }

    // Set the LED
    digitalWrite(diagLED, ledState);

    return;
  }
#endif

// Increment our timer.
void rollTimer() {
  sampleTimer++;
  
  return;
}

// ***********************
// * Setup and execution *
// ***********************

// Board setup.
void setup() {
  // Spin up console
  Serial.begin(baudRate);

  // Print boot message.
  Serial.print("Booting fw ver ");
  Serial.print(versionMajor);
  Serial.print(".");
  Serial.print(versionMinor);
  Serial.println("...");
  
  // Set up the debug LED.
  pinMode(diagLED, OUTPUT);
  digitalWrite(diagLED, ledState);
  
  // Init our I2C register
  i2cBuff[i2c_fwMajor] = versionMajor;
  i2cBuff[i2c_fwMinor] = versionMinor;

  // Set the I2C status register to reflect we're doing our initial poll
  setI2CStat(i2cStatus_initpoll);
  
  // Set the I2C status register to include all installed instruments, and print message.
  #ifdef hasRain
    setI2CStat(i2cStatus_rain);
    Serial.println("Rain sensor installed");
  #endif
  
  #ifdef hasWind
    setI2CStat(i2cStatus_wind);
    Serial.println("Wind sensor installed");
  #endif
  
  #ifdef hasLight
    setI2CStat(i2cStatus_light);
    Serial.println("Light sensor installed");
  #endif
  
  // Set up our I2C bus
  Wire.begin(myAddr);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  
  // Print I2C message
  Serial.print("Listening on I2C addr 0x");
  Serial.println(myAddr, HEX);
  
  // Configure Timer1's carry pins.
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
}

// Main execution body
void loop() {
  // Use this to keep track of hits/sample for rain sensor
  int rainVal = 0;
  
  // Use this to keep track of the wind sensor.
  int windVal = 0;
  
  // Use this to keep a running average of wind value
  unsigned long windAvg = 0;
  
  // Use this to keep track of the fastest wind speed we read.
  int windMax = 0;
  
  // Use this to keep track of the ambient light value we read.
  int lightVal = 0;
  
  // Use this to keep a running average of the ambient light value we read.
  unsigned long lightAvg = 0;

  // Use this to keep track of the offset between our
  // calibrated laser brightness and the last reading from the CdS cell.
  int offsetVal = 0;
  
  // Keep track of hits per minute (roughly)
  int hits = 0;

  // Accumulate values between subsamples.
  unsigned long windAvgSubSample = 0;
  unsigned long lightAvgSubSample = 0;

  // Dump I2C registers.
  dumpI2cReg();
  
  #ifdef hasRain
    // Print main loop debug message
    Serial.print("Sleeping ");
    Serial.print(calDelay);
    Serial.println("ms, and then calibrating rain laser.");

    // Let the ADC settle before we calibrate
    delay(calDelay);
    // And calibrate
    int baseline = calibrate();

    // Debug print for calibrated light value
    Serial.print("Rain laser calibrated at ");
    Serial.println(baseline);
  #endif
  
  // Start sampling timer.
  Serial.println("Starting sampling timer.");
  Timer1.initialize(); // This runs at one second by default.
  Timer1.attachInterrupt(rollTimer); // Here we roll the timer every second.
  
  // Let 'em know we're going.
  Serial.println("Sampling sensors.");
  Serial.println();

  // Main sensor loop
  while (true) {
    
    // Set sample timer to zero.
    sampleTimer = 0;
    
    // Flag for first sample in set
    boolean firstSample = HIGH;
    
    // Sample for specified amount of time.
    while(sampleTimer < sampleTime) {
      
      // See if we've reached our subSampleSize limit.
      if(subSampleCounter == subSampleSize) {        
        // Average wind values into subsample
        windAvg += round(windAvgSubSample / subSampleSize);
        
        // Average light values into subsample
        lightAvg += round(lightAvgSubSample / subSampleSize);
        
        // Reset subsample counter
        subSampleCounter = 0;
        
        // Reset subsample averaging values
        windAvgSubSample = 0;
        lightAvgSubSample = 0;

        // Increment subsample count.
        subSampleCount++;
      }
      
      // Increment subsample counter.
      subSampleCounter++;
      
      #ifdef hasRain
        // Check the rainCdS sensor for rain data
        rainVal = analogRead(rainCdS);
      #endif
      
      #ifdef hasWind
        // Check the anemometer for wind speed.
        windVal = analogRead(anemometer);
        
        // Stack wind speed value on the subsample.
        windAvgSubSample += windVal;
        
        // Do we have a record wind speed for this sample set?
        if (windVal > windMax) {
          windMax = windVal;
        }
      #endif

      #ifdef hasLight
        // Stack light value on the subsample.
        lightAvgSubSample += analogRead(lightCdS);
      #endif

      #ifdef hasRain
        // Compute offset value from baseline.
        offsetVal = rainVal - baseline;
      
        // If enough light is refracted (based on dropThresh)
        // Increment the rain counter.
        if (offsetVal < dropThresh) {
          // Increment our hit counter
          hits++;
          // And flicker the diagnostic LED.
          strobe();
        }
      #endif
      
      // Wait 1ms before next sample.
      delay(1);
    }
    
    // Set our global "last sample" data.
    #ifdef hasRain
      rainSample = hits;
    #endif
    
    // Debug print before modifying sample counts
    Serial.print("Samples:   ");
    Serial.println((subSampleCount * subSampleSize) + subSampleCounter);
    
    // If we have extra subsamples increment the sample count
    if(subSampleCounter > 0) {
      // Bump the subSampleCount
      subSampleCount++;
      
      #ifdef hasWind
       // Add the straggler wind sample average to the master wind average
       windAvg += (windAvgSubSample / subSampleCounter);
      #endif
      
      #ifdef hasLight
        // Add the straggler light sample average to the master light average
        lightAvg += (lightAvgSubSample / subSampleCounter);
      #endif
    }
    
    #ifdef hasWind
      // Average the wind samples.
      windSample = round(windAvg / subSampleCount);
      
      // Set the wind max.
      windSampleMax = windMax;
    #endif
    
    #ifdef hasLight
      // Average the light samples.
      lightAvg = round(lightAvg / subSampleCount);
      
      // Map to an 8-bit number.
      lightSample = map(lightAvg, 0, 1023, 0, 255); // Convert to 8 bits.
    #endif
    
    // Ensure our init poll flag is clear and set no data
    // since we don't want corrupt data if we're asked for
    // data in the middle of chaning our registers.
    clearI2CStat(i2cStatus_initpoll);
    clearI2CStat(i2cStatus_data);
        
    // Put our rain samples in the buffer.
    i2cBuff[i2c_rainMSB]  = (rainSample & 0xff000000) >> 24;
    i2cBuff[i2c_rain2SB]  = (rainSample & 0x00ff0000) >> 16;
    i2cBuff[i2c_rain3SB]  = (rainSample & 0x0000ff00) >> 8;
    i2cBuff[i2c_rainLSB]  = rainSample &  0x000000ff;
    
    // Put our wind average and max in the buffer.
    i2cBuff[i2c_windAvgMSB]  = (windSample & 0xff00) >> 8;
    i2cBuff[i2c_windAvgLSB]  = windSample &  0x00ff;
    i2cBuff[i2c_windMaxMSB]  = (windSampleMax & 0xff00) >> 8;
    i2cBuff[i2c_windMaxLSB]  = windSampleMax  & 0x00ff;
    
    // Put our ambinet light average in the buffer.
    i2cBuff[i2c_lightAvg] = lightSample;
    
    // Now we're ready. Set valid data.
    setI2CStat(i2cStatus_data);
    
    // Debug print
    Serial.print("Rain CPM:  ");
    Serial.println(rainSample);
    Serial.print("Wind Avg:  ");
    Serial.println(windSample);
    Serial.print("Wind Max:  ");
    Serial.println(windSampleMax);
    Serial.print("Light Avg: ");
    Serial.println(lightSample);
    dumpI2cReg();
    Serial.println();
    
    // Reset our sample-taking vars.
    hits = 0;
    windAvg = 0;
    windMax = 0;
    lightAvg = 0;
    subSampleCount = 0;
    subSampleCounter = 0;
  }
}

