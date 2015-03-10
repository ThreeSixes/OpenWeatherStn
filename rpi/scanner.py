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
    owsScanner - the OpenWeatherStn sensor scanner accepts one argument, magOffset a number in degrees between 0 and 359 which represents a bearing - argument defaults to zero if not specified.
    """
    
    def __init__(self, magOffset = 0):
        # Magnetic offset value
        self.magOffset = magOffset
        
        # Initialize our sensor classes.
        self.magSens = hmc5883l()
        self.cmpdSens = compoundSensor(67, 0x64)
    
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
        # to return a normal heading from 0-259 degrees.
        if heading < 0:
            heading = 360 - heading
        
        # Subtract the offset from our heading.
        heading = heading - magOffset
        
        # Round to one decimal place, and return.
        return round(heading, 1)

scanner = owsScanner()

pprint(scanner.getWindDir(scanner.magOffset))