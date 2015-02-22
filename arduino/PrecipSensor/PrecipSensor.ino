// Laser precipitation sensor by ThreeSixes
// https://github.com/ThreeSixes/OpenWeatherStn
// LICENSE?

// Include I2C support for communicating with
// our data collector.
#include <Wire.h>

// I/O config
#define photoCell 0
#define diagLED 13
#define baudRate 9600

// I2C address info
#define myAddr 0x64

// Drop threshold config
#define dropThresh -6

// Global vars
boolean ledState = LOW;
unsigned long lastSample = 0;

// Board setup.
void setup() {
  // Spin up console
  Serial.begin(baudRate);

  // Print boot message.
  Serial.println("Booting...");
  
  // Set up the debug LED.
  pinMode(diagLED, OUTPUT);
  digitalWrite(diagLED, ledState);
  
  // Set up our I2C bus
  Wire.begin(myAddr);
  Wire.onRequest(sendCPM);
  
  // Print I2C message.
  Serial.print("Listening on I2C addr 0x");
  Serial.println(myAddr, HEX);
}

// Calibrate the CdS cell
int calibrate() {
  // Read the CdS cell.
  int retVal = analogRead(photoCell);

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

// Return CPM value to I2C master.
void sendCPM() {
  // Send our last minute worth of samples.
  Wire.write(lastSample);
  
  return;
}

// Main execution body

void loop() {
  // Use this to keep track of hits/sample
  int val = 0;

  // Use this to keep track of the offset between our
  // calibrated laser brightness and the last reading from the CdS cell.
  int offsetVal = 0;
  
  // Keep track of hits per minute (roughly)
  int hits = 0;

  // Print main loop debug message
  Serial.println("Sleeping 250 ms, and then calibrating.");

  // Let the ADC settle before we calibrate
  delay(250);
  // And calibrate
  int baseline = calibrate();

  // Debug print for calibrated light value
  Serial.print("Calibrated at ");
  Serial.println(baseline);

  // Let 'em know we're going.
  Serial.println("Sampling.");

  // Main sensor loop
  while (true) {
    
    // Sample for (roughly) 1 min.
    for(long i = 0; i <= 60000; i++) { 
      // Check the photocell
      val = analogRead(photoCell);

      // Compute offset value from baseline.
      offsetVal = val - baseline;

      // If enough light is refracted (based on dropThresh)
      // Increment the counter.
      if (offsetVal < dropThresh) {
        // Increment our hit counter
        hits++;
        // And flicker the diagnostic LED.
        strobe();
        
        // Dump hits/sample
        
        //Serial.print("Hits: ");
        //Serial.println(hits);
        
      }
      
      // Wait 1ms before next sample.
      delay(1);
    }
    
    // Set our global value for the last sample count
    lastSample = hits;
    
    // Debug print
    Serial.print("CPM: ");
    Serial.println(lastSample);
    
    // Reset our hit counter.
    hits = 0;
  }
}

