# OpenWeatherStn data layer by ThreeSixes (https://github.com/ThreeSixes/OpenWeatherStn)

###########
# Imports #
###########

# Add SQLite3 support
import sqlite3

#################
# owsData class #
#################

class owsData:
    """
    owsData is a data layer class to manage data access for the OpenWeatherStn project:
        
    dbFile is a string containing the path to the weather Sqlite3 database file.
    """
    
    def __init__(self, dbFile = "db/weather.db"):
        try:
            # Connect to our SQLite database and create an object we can use to interact with it,
            # and make sure the Sqlite 3 doesn't do the thread check since we're only using one thread.
            self.__dbConn = sqlite3.connect(dbFile, detect_types = sqlite3.PARSE_DECLTYPES, check_same_thread = False)
            self.__db = self.__dbConn.cursor()
        
        # Pass any exception we get straight through.
        except Exception as e:
            raise e
    
    def __getPast(self, endingPoint):
        """
        __getPast(startingPoint, endingPoint)
        
        Get data from the past stating at a date time stamp and ending with another.
        
        *** NOT YET IMPLEMENTED ***
        """
        
        retVal = None
        
        return retVal
    
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
    
    def getLastRecord(self):
        """
        getLastRecord()
        
        Pull the latest record from the database in the following tuple order:
        
        ("dts", "temp", "humid", "baro", "rain", "windDir", "windAvg", "windMax", "lightLvl", "sysTemp")
        
        Any value except dts can be null.
        """
        
        try:
            # Pull the most recent data point.
            self.__db.execute("SELECT * FROM weather WHERE dts = (SELECT MAX(dts) FROM weather);")
            
            return self.__db.fetchone()
            
        except Exception as e:
            raise e
    