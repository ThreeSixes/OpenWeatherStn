# OpenWeatherStn sensor scanning utlity by ThreeSixes (https://github.com/ThreeSixes/OpenWeatherStn)

###########
# Imports #
###########

# We need to do some trig.
import math

# Load sensor module support.
from hmc5883l import hmc5883l
from am2315 import am2315
from compoundSensor import compoundSensor

# Pretty print
from pprint import pprint

####################
# owsScanner class #
####################

class owsScanner:
    """
    owsScanner - the OpenWeatherStn sensor scanner class. Accepts two optional arguments.
    
    magOffset: a number in degrees between 0 and 359 which represents the bearing of the sensor. This defaults to 0 (true north) if not set.
    windOffset: a number that specifies the DC offset (ADC reading as int) of the anemometer when standing still. This defaults to 67.
    """
    
    def __init__(self, magOffset = 0, windOffset = 67):
        # Sensor heading offset to get accurate wind direction data.
        self.__magOffset = magOffset
        
        # Set up our sensor objects
        self.windDirSens = hmc5883l()
        self.cmpdSens = compoundSensor(windOffset)
        self.tempHumid = am2315()
        
        # Track temp and humidity data from our am2315.
        self.__thData = []
    
    def getWindDir(self):
        """
        getWindDir()
        
        Get the heading of the wind in degrees. Returns an integer rounded to one decimal place.
        """
        
        # Magnetic sensor data (X, Z, Y)
        magData = [0, 0, 0]
        
        # Configure magnetometer - no sample averaging, default 15 updates per second, no biasing,
        #  the lowest gain supported (230mG/LSB keeps the sensor for saturating),
        #  and to automatically take constant readings.
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
        
        # Round to one decimal place, and wind heading relative to our offset.
        return round(offsetHeading, 1)
    
    def pollCmpdSens(self):
        """
        pollCmpdSens()
        
        Poll the compound wind sensor to get data from it. This must be executed before getWindAvgSpeed(), getWindMaxSpeed(), getRainCount(), and getAmbientLight().
        """
        
        self.cmpdSens.pollAll()
    
    def getWindAvgSpeed(self):
        """
        getWindAvgSpeed()
        
        Gets the average wind speed from the compound sensor. Returns an integer expressing wind speed in kph, rounded to two digits - or "None" if the sensor is not installed.
        """
        
        retVal = None
        
        # If our sensor reports having an anemometer module installed get the value.
        if self.cmpdSens.checkStatusReg(self.cmpdSens.i2cStatus_wind):
            retVal = self.cmpdSens.getWindAvg()
        
        return retVal
    
    def getWindMaxSpeed(self):
        """
        getWindMaxSpeed()
        
        Gets the max wind speed from the compound sensor. Returns an integer expressing wind speed in kph, rounded to two digits - or "None" if the sensor is not installed.
        """
        
        retVal = None
        
        # If our sensor reports having an anemometer module installed get the value.
        if self.cmpdSens.checkStatusReg(self.cmpdSens.i2cStatus_wind):
            retVal = self.cmpdSens.getWindMax()
        
        return retVal
    
    def getRainCount(self):
        """
        getRainCount()
        
        Gets the rain counter value from the compound sensor. Returns a 32 bit integer - or "None" if the sensor is not installed.
        """
        
        retVal = None
        
        # If our sensor reports having the rain module installed get the value.
        if self.cmpdSens.checkStatusReg(self.cmpdSens.i2cStatus_rain):
            retVal = self.cmpdSens.getRainCount()
        
        return retVal
    
    def getAmbientLight(self):
        """
        getAmbientLight()
        
        Gets the ambient light average from the compound sensor module. Returns an 8-bit unsigned number - or "None" if the light sensor is not installed.
        """
        retVal = None
        
        # If our sensor reports having the light module installed get the value.
        if self.cmpdSens.checkStatusReg(self.cmpdSens.i2cStatus_light):
            retVal = self.cmpdSens.getLightAvg()
        
        return retVal
    
    def pollTempHumid(self):
        """
        pollTempHumid()
        
        Poll the AM2315 sensor to get temeperature and humidity data. This must be run before getTemp() and getHumid().
        """
        
        self.__thData = self.tempHumid.getTempHumid()
    
    def getTemp(self):
        """
        getTemp()
        
        Get temperature in degrees celcius from weather temperature sensor. Returns an integer rounded to 1 decimal point.
        """
        
        return self.__thData[0]
    
    def getHumid(self):
        """
        getHumid()
        
        Get relative humidity as a percentage from the weather humidity sensor. Returns and integer rounded to 1 decimal point.
        """
        
        return self.__thData[1]
    

#######################
# Main execution body #
#######################

# Set up our scanner object.
scanner = owsScanner()

# System test.
print(" + Open Weather Station sensor scan test +")
print("Checking compound sensor...")

# Poll the compound sensor before displaying data from it.
scanner.pollCmpdSens()

print("Average wind speed: " + str(scanner.getWindAvgSpeed()))
print("Maximum wind speed: " + str(scanner.getWindMaxSpeed()))
print("Rain counter:       " + str(scanner.getRainCount()))
print("Ambient light:      " + str(scanner.getAmbientLight()))
# Check the wind direciton.
print("Checking wind vein...")
print("Wind direction:     " + str(scanner.getWindDir()))

# Check the temperature and humidity.
print("Checking temperature and humdity...")

# Poll the AM2315 to get temperature and humidity data.
scanner.pollTempHumid()

print("Temperature (C):   " + str(scanner.getTemp()))
print("Humidity (%RH):    " + str(scanner.getHumid()))

# Check barometer.
print("Checking barometer...")
print("-> Module not supported.")

# Check system temperature.
print("Checking system temperature...")
print("-> Module not supported.")

print("")
