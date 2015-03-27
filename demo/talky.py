import urllib.request
import urllib.parse
import json
from pprint import pprint
from subprocess import call

apiURL = 'http://weatherstn'

def wordify(sourceDict):
    """
    wordify(sourceDict)
   
    Convert units to words, and trim values to have them more easily spoken.
    """
   
    # Loop through our data, modifying values.
    for point in sourceDict:
        # Don't try to handle the timestamp here.
        if point != 'dts':
            # Handle values in C
            if sourceDict[point]['unit'] == "C":
                sourceDict[point]['unit'] = "celsius"
                sourceDict[point]['value'] = str(round(sourceDict[point]['value'], 0)).replace('.0', '')
           
            # Handle values in F
            if sourceDict[point]['unit'] == "F":
                sourceDict[point]['unit'] = "fahrenheit"
                sourceDict[point]['value'] = str(round(sourceDict[point]['value'], 0)).replace('.0', '')
               
            # Handle values in kph
            if sourceDict[point]['unit'] == "kph":
                sourceDict[point]['unit'] = "kilometers per hour"
                sourceDict[point]['value'] = str(round(sourceDict[point]['value'], 0)).replace('.0', '')
           
            # Handle values in mph
            if sourceDict[point]['unit'] == "mph":
                sourceDict[point]['unit'] = "miles per hour"
                sourceDict[point]['value'] = str(round(sourceDict[point]['value'], 0)).replace('.0', '')
               
            # Handle humidity
            if point == "humid":
                sourceDict[point]['unit'] = "percent"
                sourceDict[point]['value'] = str(round(sourceDict[point]['value'], 0)).replace('.0', '')
               
            # Handle wind direction
            if point == "windDirCrd":
                sourceDict[point]['value'] = sourceDict[point]['value'].replace('N', 'north ').replace('S', 'south ').replace('E', 'east ').replace('W', 'west ')
   
    return sourceDict


# Holders for our data.
jsonBytes = None
jsonStr = None
weatherData = None
speakWeather = None


# Set up parameters with the data points we want to request.
params = json.dumps({'extra': 'computed', 'units': 'standard'})
binParams = params.encode('ascii')

try:
    # Try to pull the data down.
    f = urllib.request.urlopen(apiURL, binParams)
   
    # Read the data returned to us.
    jsonBytes = f.read()
   
except urllib.error.HTTPError:
    print("Caught HTTP error")
   
except Exception as e:
    raise e

# Decode the bytes we get as a UTF-8 string.
jsonStr = jsonBytes.decode(encoding='UTF-8')

# Wrap the JSON up in a dict.
weatherData = json.loads(jsonStr)
weatherData = wordify(weatherData)

# Build the weather report
speakWeather = "The temperature is " + weatherData['temp']['value'] + " degrees " + weatherData['temp']['unit'] + \
    " with " + weatherData['humid']['value'] + " " + weatherData['humid']['unit'] + " humidity. The wind is " + \
    weatherData['windAvgSpd']['value'] + " " + weatherData['windAvgSpd']['unit'] + " from the " + \
    weatherData['windDirCrd']['value'] + " with gusts up to " + weatherData['windMaxSpd']['value'] + " " + \
    weatherData['windMaxSpd']['unit']

# Run espeak
call(["espeak", speakWeather])

"""
{'baro': {'name': 'Barometric pressure', 'unit': 'kPa', 'value': 101.81},
 'dts': '2015-03-24 19:23:32.336780',
 'humid': {'name': 'Humidity', 'unit': '%RH', 'value': 61},
 'lightAmb': {'name': 'Ambient light', 'unit': None, 'value': 62},
 'rainCt': {'name': 'Rain intensity', 'unit': 'counts', 'value': 0},
 'sysTemp': {'name': 'System temperature', 'unit': 'celsius', 'value': 21.3},
 'temp': {'name': 'Temperature', 'unit': 'celsius', 'value': 21.3},
 'windAvgSpd': {'name': 'Average wind speed',
                'unit': 'kilometers per hour',
                'value': 0},
 'windDir': {'name': 'Wind direction', 'unit': 'degrees', 'value': 217.3},
 'windMaxSpd': {'name': 'Maximum wind speed',
                'unit': 'kilometers per hour',
                'value': 0.3}}
"""
