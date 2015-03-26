# OpenWeatherStn data layer test by ThreeSixes (https://github.com/ThreeSixes/OpenWeatherStn)

###########
# Imports #
###########

import datetime
from owsData import owsData
from pprint import pprint

########################
# Main execution body #
########################

dl = owsData()

lastRecord = dl.getLastRecord()

print("Got record from: " + str(lastRecord[0]))
pprint(lastRecord)
