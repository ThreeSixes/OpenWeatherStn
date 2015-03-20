# OpenWeatherStn weather service layer by ThreeSixes (https://github.com/ThreeSixes/OpenWeatherStn)

###########
# Imports #
###########

import json
import datetime
from owsData import owsData
from pprint import pprint

########################
# Main execution body #
########################

# Load data layer.
dl = owsData()

# Figoure out our mode.
modeJson = False

# Pull the last record as a tuple
lastRecord = dl.getLastRecord()

# Grab the date time stamp for processing as a string.
dts = str(lastRecord[0])

# Zero-fill the string in the event we don't have ms specified.
# For consistency.
if len(dts) == 19:
    dts = dts + ".000000"

def htmlify(weatherDict):
    """
    htmlify(weatherDict)
    
    Convert data to an HTML page.
    """
    # HTML header
    body = "<HTML>\n<HEAD>\n<TITLE>OpenWeatherStn live data</TITLE>\n</HEAD>\n<BODY>\n"
    
    # Build page with data.
    
    # HTML footer
    body = body + "</BODY>\n</HTML>"
    
    # Dump page.
    print(body)

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
if(modeJson):
    # Build JSON string from dict.
    jsonRecord = json.dumps(lastRecord)

    # Dump JSON string.
    print(jsonRecord)
else:
    htmlify(lastRecord)