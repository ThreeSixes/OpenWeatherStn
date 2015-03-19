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

# Thereading support
import threading

# Import support for timing
import time

# Load sensor module support.
from hmc5883l import hmc5883l
from am2315 import am2315
from mpl115a2 import mpl115a2
from mcp9808 import mcp9808
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
    windOffset: a number that specifies the DC offset (ADC reading as int) of the anemometer when standing still. This defaults to 79.
    """
    
    def __init__(self, magOffset = 0, windOffset = 79):
        # Sensor heading offset to get accurate wind direction data.
        self.__magOffset = magOffset
        
        # Set up our sensor objects
        self.windDirSens = hmc5883l()
        self.cmpdSens = compoundSensor(windOffset)
        self.tempHumid = am2315()
        self.baroSens = mpl115a2()
        self.sysThermo = mcp9808()
        
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
    
    def getWindAvgRaw(self):
        """
        getWindAvgRaw()
        
        Gets the average wind raw data from the compound sensor. Returns an unsigned integer with 10 bits of data representing the average raw ADC reading for the last sample period. Returns None of the anemometer isn't installed.
        """
        
        retVal = None
        
        # If our sensor reports having an anemometer module installed get the value.
        if self.cmpdSens.checkStatusReg(self.cmpdSens.i2cStatus_wind):
            retVal = self.cmpdSens.getWindAvgRaw()
        
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
    
    def getWindMaxRaw(self):
        """
        getWindMaxRaw()
        
        Gets the max wind raw data from the compound sensor. Returns an unsigned integer with 10 bits of data representing the max raw ADC reading for the last sample period. Returns None of the anemometer isn't installed.
        """
        
        retVal = None
        
        # If our sensor reports having an anemometer module installed get the value.
        if self.cmpdSens.checkStatusReg(self.cmpdSens.i2cStatus_wind):
            retVal = self.cmpdSens.getWindMaxRaw()
        
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
        
        Get barometirc pressure in kPa. Returns a number rounded to two decimal points.
        """
        
        retVal = self.baroSens.getPressTemp()
        
        return retVal[0]
    
    def getSysTemp(self):
        """
        getSysTemp()
        
        Gets the system temperature in degrees C, up to four decimal places.
        """
        
        return self.sysThermo.getAmbientTemp()

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
            self.__dbConn = sqlite3.connect(dbFile, detect_types=sqlite3.PARSE_DECLTYPES)
            self.__db = self.__dbConn.cursor()
        
        # Pass any exception we get straight through.
        except Exception as e:
            raise e
    
    def addRecord(self, values):
        """
        addRecord(values)
        
        Add a record to the database containing the information in values. Values should be a tuple containing the following elements:
        
        ("dts", "temp", "humid", "baro", "rain", "windDir", "windAvg", "windMax", "lightLvl", "sysTemp")
        
        Null values for any of these keys, except dts are acceptable.
        """
        
        try:
            self.__db.execute('INSERT INTO weather(dts, temp, humid, baro, rain, windDir, windAvg, windMax, lightLvl, sysTemp) VALUES(?,?,?,?,?,?,?,?,?,?);', values)
            self.__dbConn.commit()
            
        except Exception as e:
            raise e

################
# Worker class #
################

class worker(threading.Thread):
    """
    Worker class - main execution thread
    """
    
    def __init__(self):
        print("Init worker thread.")
        threading.Thread.__init__(self)
        
        # Pull in necessary objects.
        self.dl = dataLayer()
        self.scanner = scanner()
        
    def displayRecord(self, allData, rawWind):
        """
        displayRecord(allData, rawWind)
        
        Display data from readings for debugging and testing.
        """
        
        # System test.
        print(" + Open Weather Station sensor scan test +")
        
        print("\nExecution time:")
        print("-> " + str(allData[0]))
        
        print("\nChecking compound sensor...")
        
        print("-> Average wind speed (kph): " + str(allData[6]))
        print("-> Maximum wind speed (kph): " + str(alldata[7]))
        print("-> Average wind raw value:   " + str(rawWind[0]))
        print("-> Maximum wind raw value:   " + str(rawWind[1]))
        
        print("-> Rain counter:             " + str(allData[4]))
        print("-> Ambient light:            " + str(allData[8]))
        
        # Check the wind direciton.
        print("\nChecking wind vein...")
        print("-> Wind direction (deg):     " + str(allData[5]))
        
        # Check the temperature and humidity.
        print("\nChecking temperature and humdity...")
        
        print("-> Temperature (C):          " + str(allData[1]))
        print("-> Humidity (%RH):           " + str(allData[2]))
        
        # Check barometer.
        print("\nChecking barometer...")
        print("-> Barometirc press. (kPa):  " + str(allData[3]))
        
        # Check system temperature.
        print("\nChecking system temperature...")
        print("-> System temperature (C):   " + str(allData[9]))
        
        print("")
    
    def run(self):
        """
        run(self)
        
        Principal method in thread. The work is done here.
        """
        
        # Set loop control var #1
        noSuccess = True
        
        # Set loop control var #2
        attemptCount = 0
        
        # Try to read the compound sensor until we have good data OR we fail twice.
        while(noSuccess and attemptCount < 2):
            try:
                # Poll the compound sensor and grab data from it.
                self.scanner.pollCmpdSens()
                
                # Grab sensor data.
                windAvgSpd = self.scanner.getWindAvgSpeed()
                windMaxSpd = self.scanner.getWindMaxSpeed()
                windAvgRaw = self.scanner.getWindAvgRaw()
                windMaxRaw = self.scanner.getWindMaxRaw()
                rainCt = self.scanner.getRainCount()
                lightAmb = self.scanner.getAmbientLight()
                
                # If nothing has blown up so far, flag the loop to exit.
                noSuccess = False
            
            except Exception as e:
                # D'oh. Log the exception or something.
                print("Exception trying to poll compound sensor:")
                pprint(e)
                
                # Increment our attempt counter.
                attemptCount = attemptCount + 1
            
        # If we didn't get good data, set everything to None to keep the program from blowing up.
        if noSuccess:
            windAvgSpd, windMaxSpd, windAvgRaw, windMaxRaw, rainCt, lightAmb = None
        else:
            # If we failed reset noSuccess for the next sensor.
            noSuccess = True
        
        # Reset the attempt counter.
        attemptCount = 0
        
        # Try to read the wind vein sensor until we have good data OR we fail twice.
        while(noSuccess and attemptCount < 2):
            try:
                # Grab sensor data.
                windDir = self.scanner.getWindDir()
                
                # If nothing has blown up so far, flag the loop to exit.
                noSuccess = False
                
            except Exception as e:
                # D'oh. Log the exception or something.
                print("Exception trying to poll wind vein:")
                pprint(e)
                
                # Increment our attempt counter.
                attemptCount = attemptCount + 1
            
        # If we didn't get good data, set everything to None to keep the program from blowing up.
        if noSuccess:
            windDir = None
        else:
            # If we failed reset noSuccess for the next sensor.
            noSuccess = True
        
        # Reset the attempt counter.
        attemptCount = 0
        
        # Try to read the temp/humidity sensor until we have good data OR we fail twice.
        while(noSuccess and attemptCount < 2):
            try:
                # Poll the compound sensor and grab data from it.
                self.scanner.pollTempHumid()
                
                # Grab sensor data.
                temperature = self.scanner.getTemp()
                humidity = self.scanner.getHumid()
                 
                # If nothing has blown up so far, flag the loop to exit.
                noSuccess = False
        
            except Exception as e:
                # D'oh. Log the exception or something.
                print("Exception trying to poll temperature and humidity sensor:")
                pprint(e)
                
                # Increment our attempt counter.
                attemptCount = attemptCount + 1
            
        # If we didn't get good data, set everything to None to keep the program from blowing up.
        if noSuccess:
            temperature, humidity = None
        else:
            # If we failed reset noSuccess for the next sensor.
            noSuccess = True
        
        # Reset the attempt counter.
        attemptCount = 0
        
        # Try to read the barometer sensor until we have good data OR we fail twice.
        while(noSuccess and attemptCount < 2):
            try:
                # Grab sensor data.
                baroPressure = self.scanner.getBaro()
                 
                # If nothing has blown up so far, flag the loop to exit.
                noSuccess = False
                
            except Exception as e:
                # D'oh. Log the exception or something.
                print("Exception trying to poll barometer:")
                pprint(e)
                
                # Increment our attempt counter.
        attemptCount = attemptCount + 1
        
        # If we didn't get good data, set everything to None to keep the program from blowing up.
        if noSuccess:
            baroPressure = None
        else:
            # If we failed reset noSuccess for the next sensor.
            noSuccess = True
        
        # Reset the attempt counter.
        attemptCount = 0
        
        # Try to read the system thermometer sensor until we have good data OR we fail twice.
        while(noSuccess and attemptCount < 2):
            try:
                # Grab sensor data.
                sysTemp = self.scanner.getSysTemp()
                
                # If nothing has blown up so far, flag the loop to exit.
                noSuccess = False
                    
            except Exception as e:
                # D'oh. Log the exception or something.
                print("Exception trying to poll system thermometer:")
                pprint(e)
                
                # Increment our attempt counter.
                attemptCount = attemptCount + 1
            
        # If we didn't get good data, set everything to None to keep the program from blowing up.
        if noSuccess:
            sysTemp = None
        else:
            # If we failed reset noSuccess for the next sensor.
            noSuccess = True
        
        # Create a tuple containing our data.
        allData = (datetime.datetime.utcnow(), temperature, humidity, baroPressure, \
                   rainCt, windDir, windAvgSpd, windMaxSpd, lightAmb, sysTemp)
        
        # Insert the tuple into the database.
        self.dl.addRecord(allData)
        self.displayRecord(allData, [windAvgRaw, windMaxRaw])


#######################
# Main execution body #
#######################

# Threading setup
threadLock = threading.Lock()
threadList = []

# Run 'till we're killed for some reason.
while(True):
    # Set up our thread.
    print("Spinning up poller thread.")
    scanThread = worker()
    scanThread.start()
    threadList.append(scanThread)
    
    # Shut the thread down when it's done.
    for t in threadList:
        t.join()
    
    # Sleeping is important because it enables us to quit with control + C, and makes sure our thread runs every 60 seconds.
    time.sleep(60)

print("Exiting.")
