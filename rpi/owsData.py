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