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
        body = "<HTML>\n<HEAD>\n<TITLE>OpenWeatherStn live data</TITLE>\n</HEAD>\n<BODY>\n"
        # Build page with data.
        # HTML footer
        body = body + "</BODY>\n</HTML>"
        
        # Return page
        return body
    
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
            "temp": {"value": lastRecord[1], "unit": "C"}, \
            "humidity": {"value": lastRecord[2], "unit": "%RH"}, \
            "baro": {"value": lastRecord[3], "unit": "kPa"}, \
            "rainCt": {"value": lastRecord[4], "unit": "count"}, \
            "windDir": {"value": lastRecord[5], "unit": "degrees"}, \
            "windAvgSpd": {"value": lastRecord[6], "unit": "kph"}, \
            "windMaxSpd": {"value": lastRecord[7], "unit": "kph"}, \
            "lightAmb": {"value": lastRecord[8], "unit": "scalar"}, \
            "sysTemp": {"value": lastRecord[9], "unit": "C"}}
        
        # JSON or HTML mode?
        if checkEnv['REQUEST_METHOD'] == 'POST':
            # Build JSON string from dict.
            jsonRecord = json.dumps(lastRecord)
            
            # Dump JSON MIME type:
            cntntType = "application/javascript"
            
            # Set body.
            body = jsonRecord
        else:
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