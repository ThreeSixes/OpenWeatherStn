# OpenWeatherStn weather service layer by ThreeSixes (https://github.com/ThreeSixes/OpenWeatherStn)

###########
# Imports #
###########

import json
import datetime
from owsData import owsData
from pprint import pprint
from wsgiref.simple_server import make_server
from wsgiref.validate import validator

########################
# weatherService class #
########################

class weatherService:
    """
    Simple HTTP service for handling weather data requests.
    """

    def __init__(self):
        self.dl = owsData() # Data layer
        self.modeJson = False # Default to JSON mode.        
    
    def __htmlify(self, weatherDict):
        """
        htmlify(weatherDict)
        
        Convert weather data to an HTML page. Returns a string.
        """
        # HTML header
        body = "<HTML>\n<HEAD>\n<TITLE>OpenWeatherStn live data</TITLE>\n</HEAD>\n<BODY style=\"font-family: sans-serif; background-color: black; color: white;\">\n"
        
        # Intro text
        body = body + "<SPAN style=\"font-size: large; font-weight: bold;\">Open Weather Station live data</SPAN>\n<BR />\n<BR />\n"
        
        # Build page with data.
        body = body + "Reading taken: " + weatherDict['dts'] + " UTC<BR />\n<BR />\n"
        
        # Start creating an output table.
        body = body + "<TABLE style=\"border: 1px solid black;\">\n"
        
        # Get all the weathers!
        for key in ["temp", "humid", "baro", "windAvgSpd", "windMaxSpd", "windDir", "rainCt", "lightAmb", "sysTemp"]:
            if key != 'dts':
                body = body + "<TR><TD style=\"font-weight: bold;\">" + weatherDict[key]['name'] + "</TD><TD>" + str(weatherDict[key]['value'])
                if weatherDict[key]['unit'] != None: body = body + " " + weatherDict[key]['unit']
            
            body = body + "</TD></TR>\n"
        
        # HTML footer
        body = body + "</TABLE>\n</BODY>\n</HTML>"
        
        # Return page
        return body
    
    def __toStandard(self, data):
        """
        __toStandard(data)
        
        Converts all metric readings into standard/imperial units. Returns a dict.
        """
        
        # Loop through our data, looking for C, kph, kPa
        for point in data:
            # Don't try to handle the timestamp here.
            if point != 'dts':
                # Convert a celcius temp to farenheit
                if data[point]['unit'] == "C":
                    data[point]['unit'] = "F"
                    data[point]['value'] = round((data[point]['value'] * 9.0) / 5.0 + 32.0, 3)
                
                # Convert pressure in kilopascals to inches of mercury.
                if data[point]['unit'] == "kPa":
                    data[point]['unit'] = "inHg"
                    data[point]['value'] = round(data[point]['value'] * 0.295333727, 1)
                
                # Convert velocity from kph to mph.
                if data[point]['unit'] == "kph":
                    data[point]['unit'] = "mph"
                    data[point]['value'] = round(data[point]['value'] * 0.621371, 2)
        
        return data
    
    def worker(self, env, startResponse):
        """
        worker(evn, startResponse)
        
        Do all the things. Accepts two arguments: the environment data, and start_server from WSGI.
        """
        
        # Grab our enviornment data
        checkEnv = env.copy()
        
        # Dummy string to hold the text body.
        body = ""
        
        # Pull the most recent record from the data layer.
        lastRecord = self.dl.getLastRecord()
        
        # Grab the date time stamp for processing as a string.
        dts = str(lastRecord[0])
        
        # Zero-fill the string in the event we don't have ms specified.
        # For consistency.
        if len(dts) == 19:
            dts = dts + ".000000"
            
        # Build dict for JSONification.
        lastRecord = {"dts": dts, \
            "temp": {"name": "Temperature", "value": lastRecord[1], "unit": "C"}, \
            "humid": {"name": "Humidity", "value": lastRecord[2], "unit": "%RH"}, \
            "baro": {"name": "Barometric pressure", "value": lastRecord[3], "unit": "kPa"}, \
            "rainCt": {"name": "Rain intensity", "value": lastRecord[4], "unit": "counts"}, \
            "windDir": {"name": "Wind direction", "value": lastRecord[5], "unit": "degrees"}, \
            "windAvgSpd": {"name": "Average wind speed", "value": lastRecord[6], "unit": "kph"}, \
            "windMaxSpd": {"name": "Maximum wind speed", "value": lastRecord[7], "unit": "kph"}, \
            "lightAmb": {"name": "Ambient light", "value": lastRecord[8], "unit": None}, \
            "sysTemp": {"name": "System temperature", "value": lastRecord[9], "unit": "C"}}
        
        # JSON or HTML mode?
        if checkEnv['REQUEST_METHOD'] == 'POST':
            # Build JSON string from dict.
            jsonRecord = json.dumps(lastRecord)
            
            # Dump JSON MIME type:
            cntntType = "application/javascript"
            
            # Set body.
            body = jsonRecord
        else:
            # See if we asked for different units.
            if '/standard' in checkEnv['PATH_INFO']:
                lastRecord = self.__toStandard(lastRecord)
            
            # Dump HTML MIME type
            cntntType = "text/html"
            
            # Gather HTML
            body = self.__htmlify(lastRecord)
        
        # Set a generic HTTP 200 status
        status = "200 OK"
        
        # Set content type header
        headers = [('Content-Type', cntntType)]
        
        # Start returning the page
        startResponse(status, headers)
        
        # Send the output back to our web server.
        return [bytes(body, 'utf-8')]


#######################
# Main execution body #
#######################

# Utilize our worker class
hardWorker = weatherService()

# Validator
validatorApp = validator(hardWorker.worker)

# Set up HTTP server
httpSrv = make_server('', 80, validatorApp)
print("weatherService HTTP server listening on port 80.")
httpSrv.serve_forever()