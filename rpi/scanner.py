###########
# Imports #
###########

# We need to do some trig.
import math

# Load sensor module support.
from hmc5883l import hmc5883l
from compoundSensor import compoundSensor

# Pretty print
from pprint import pprint

####################
# owsScanner class #
####################

class owsScanner:
    """
    owsScanner - the OpenWeatherStn sensor scanner accepts two arguments: magOffset a number in degrees between 0 and 359 which represents a bearing - argument defaults to zero if not specified, and windOffset which is an integer that specifies the DC offset of the anemometer when standing still.
    """
    
    def __init__(self, magOffset = 0, windOffset = 67):
        # Sensor heading offset to get accurate wind direction data.
        self.__magOffset = magOffset
        
        # Set up our sensor objects
        self.windDirSens = hmc5883l()
        self.cmpdSens = compoundSensor(windOffset)
    
    def getWindDir(self):
        """
        getWindDir()
        
        Get the heading of the wind in degrees. Returns an integer rounded to one decimal place.
        """
        
        # Magnetic sensor data (X, Z, Y)
        magData = [0, 0, 0]
        
        # Configure magnetometer
        self.windDirSens.setReg(self.windDirSens.regCfgA, (self.windDirSens.avg1 | self.windDirSens.freq15 | self.windDirSens.biasNone))
        self.windDirSens.setReg(self.windDirSens.regCfgB, self.windDirSens.gain230)
        self.windDirSens.setReg(self.windDirSens.regMode, self.windDirSens.modeCont)
        
        # Get data from the magentometer.
        magData = self.windDirSens.getXZY()
        
        # Compute heading as a cartesian value given data on the X, Y planes. Heading is relative to the sensor, not north.
        heading = math.atan2(magData[0], magData[2]) * 180.0 / math.pi
        
        # Since the heading is reported from -180 to +180 make sure we compensate for that fact
        # to return a normal heading from 0 - 359 degrees.
        if heading < 0:
            heading = 360 - abs(heading)
        
        # Add offset to heading, to adjust for the weather station's orientation relative to north.
        offsetHeading = heading + self.__magOffset
        
        # If our offset heading wraps around the heading "circle" compensate for it.
        if offsetHeading > 360:
            offsetHeading = offsetHeading - 360
        
        # Round to one decimal place, and return.
        return round(offsetHeading, 1)
    
    def getWindAvgSpeed(self):
        """
        getWindAvgSpeed()
        
        Gets the average wind speed from the compound sensor. Returns an integer expressing wind speed in kph, rounded to two digits or "None" if the sensor is not installed.
        """
        
        retVal = None
        
        # If our sensor reports having an anemometer installed get the value.
        if self.cmpdSens.checkStatusReg(self.cmpdSens.i2cStatus_wind):
            retVal = self.cmpdSens.getWindAvg()
        
        return retVal
    
    def getWindMaxSpeed(self):
        """
        getWindMaxSpeed()
        
        Gets the max wind speed from the compound sensor. Returns an integer expressing wind speed in kph, rounded to two digits or "None" if the sensor is not installed.
        """
        
        retVal = None
        
        # If our sensor reports having an anemometer installed get the value.
        if self.cmpdSens.checkStatusReg(self.cmpdSens.i2cStatus_wind):
            retVal = self.cmpdSens.getWindMax()
        
        return retVal
    
    def getRainCount(self):
        """
        getRainCount()
        
        Gets the rain counter value from the compound sensor. Returns a 32 bit integer or "None" if the sensor is not installed.
        """
        
        retVal = None
        
        # If our sensor reports having the rain sensor installed get the value.
        if self.cmpdSens.checkStatusReg(self.cmpdSens.i2cStatus_rain):
            retVal = self.cmpdSens.getRainCount()
        
        return retVal
    
    def getAmbientLight(self):
        """
        getAmbientLight()
        
        Gets the ambient light average from the compound sensor module. Returns an 8-bit unsigned number or "None" if the light sensor is not installed.
        """
        retVal = None
        
        # If our sensor reports having the light sensor installed get the value.
        if self.cmpdSens.checkStatusReg(self.cmpdSens.i2cStatus_light):
            retVal = self.cmpdSens.getLightAvg()
        
        return retVal
    

#######################
# Main execution body #
#######################

scanner = owsScanner()

print(" + Open Weather Station sensor scanner results +")
print("Wind direction:     " + str(scanner.getWindDir()))
print("Average wind speed: " + str(scanner.getWindAvgSpeed()))
print("Maximum wind speed: " + str(scanner.getWindMaxSpeed()))
print("Rain counter:       " + str(scanner.getRainCount()))
print("Ambient light:      " + str(scanner.getAmbientLight()))
print("")
