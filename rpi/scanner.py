# OpenWeatherStn sensor scanning utlity by ThreeSixes (https://github.com/ThreeSixes/OpenWeatherStn)

###########
# Imports #
###########

# We need to do some trig.
import math

# Add SQLite3 support
import sqlite3

# Add support for date and time processing
import datetime

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
    windOffset: a number that specifies the DC offset (ADC reading as int) of the anemometer when standing still. This defaults to 75.
    """
    
    def __init__(self, magOffset = 0, windOffset = 75):
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
    
    def getBaro(self):
        """
        getBaro()
        
        Dummy method in place until support for barometric readings is added. Returns None
        """
        
        return None
    
    def getSysTemp(self):
        """
        getSysTemp()
        
        Dummy method in place until support for system temperature readings is added. Returns None
        """
        
        return None

##########################
# Data layer for scanner #
##########################

class scannerData:
    """
    scannerData is a data layer class for the sensor scanner that accepts one optional argument:
        
    dbFile is a string containing the path to the weather Sqlite3 database file.
    """
    
    def __init__(self, dbFile = "db/weather.db"):
        try:
            # Connect to our SQLite database and create an object we can use to interact with it.
            dbConn = sqlite3.connect(dbFile, detect_types=sqlite3.PARSE_DECLTYPES)
            self.db = dbConn.cursor()
        
        # Pass any exception we get straight through.
        except Exception as e:
            raise e
        
    def addRecord(self, values):
        """
        addRecord(values)
        
        Add a record to the database containing the information in values. Values should be an assoc. array containing the following elements:
        
        {"dts", "temp", "humid", "baro", "rain", "windDir", "windAvg", "windMax", "lightLvl", "sysTemp"}
        
        Null values for any of these keys, except dts are acceptable.
        """
        
        try:
            self.db.execute('INSERT INTO weather VALUES (' + values['dts'] + ',' + values['temp'] + ',' + values['humid'] + \
                            ',' + values['baro'] + ',' + values['rain'] + ',' + values['windDir'] + ',' + values['windAvg'] +  \
                            ',' + values['windMax'] + ',' + values['lightLvl'] + ',' + values['sysTemp'] + ')')
            
        except Exception as e:
            raise e

#######################
# Main execution body #
#######################

# Set up our scanner object and data layer.
scanner = owsScanner()
dl = scannerData()

# Poll sensors that require an initial poll.
scanner.pollCmpdSens()
scanner.pollTempHumid()

allData = {"dts": datetime.datetime.utcnow(), "temp": scanner.getTemp(), "humid": scanner.getHumid(), "baro": scanner.getBaro(), \
           "rain": scanner.getRainCount(), "windDir": scanner.getWindDir(), "windAvg": scanner.getWindAvgSpeed(), \
           "windMax": scanner.getWindMaxSpeed(), "lightLvl": scanner.getAmbientLight(), "sysTemp": scanner.getSysTemp()}

# Insert all the records in our weather database.
dl.addRecord(allData)

# System test.
print(" + Open Weather Station sensor scan test +")
pprint(allData)

print("Checking compound sensor...")

print("-> Average wind speed (kph): " + str(scanner.getWindAvgSpeed()))
print("-> Maximum wind speed (kph): " + str(scanner.getWindMaxSpeed()))
print("-> Rain counter:             " + str(scanner.getRainCount()))
print("-> Ambient light:            " + str(scanner.getAmbientLight()))

# Check the wind direciton.
print("\nChecking wind vein...")
print("-> Wind direction (deg):     " + str(scanner.getWindDir()))

# Check the temperature and humidity.
print("\nChecking temperature and humdity...")

print("-> Temperature (C):          " + str(scanner.getTemp()))
print("-> Humidity (%RH):           " + str(scanner.getHumid()))

# Check barometer.
print("\nChecking barometer...")
print("-> Barometirc press. (mPa):  " + str(scanner.getBaro()))

# Check system temperature.
print("\nChecking system temperature...")
print("-> System temperature (C):   " + str(scanner.getSysTemp()))

print("")
