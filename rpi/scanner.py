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
        # Anemometer ADC offset value
        self.windOffset = windOffset
        
        # Initialize our sensor classes.
        self.magSens = hmc5883l()
        self.cmpdSens = compoundSensor(windOffset, 0x64)
    
    def getWindDir(self, magOffset):
        """
        getWindDir(magOffset)
        
        Get the heading of the wind in degrees. The magOffset should be the direction the sensor is facing. This offset will change the offset in the wind vein.
        """
        
        # Magnetic sensor data
        magData = [0, 0, 0]
        
        # Configure magnetometer
        self.magSens.setReg(self.magSens.regCfgA, (self.magSens.avg1 | self.magSens.freq15 | self.magSens.biasNone))
        self.magSens.setReg(self.magSens.regCfgB, self.magSens.gain230)
        self.magSens.setReg(self.magSens.regMode, self.magSens.modeCont)
        
        # Get data from the magentometer.
        magData = self.magSens.getXZY()
        
        # Compute heading as a cartesian value given data on the x, Y planes.
        heading = math.atan2(magData[0], magData[2]) * 180.0 / math.pi
        
        # Since the heading is reported from -180 to +180 make sure we compensate for that fact
        # to return a normal heading from 0-359 degrees.
        if heading < 0:
            heading = 360 - abs(heading)
        
        # Add offset to heading
        offsetHeading = heading + offset
        
        # If our offset heading wraps around the circle compensate for that.
        if offsetHeading > 360:
            offsetHeading = offsetHeading - 360
        
        # Round to one decimal place, and return.
        return round(offsetHeading, 1)

#######################
# Main execution body #
#######################

scanner = owsScanner()

pprint(scanner.getWindDir(scanner.magOffset))
