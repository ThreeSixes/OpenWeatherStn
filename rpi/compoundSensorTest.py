from pprint import pprint
from compoundSensor import compoundSensor

# Compound sensor object, baseline wind value of 67.
cs = compoundSensor(74)

# Poll the sensor so the values in the sensor can be handled and decoded.
cs.pollAll()

# Get the readings and data we want.
print("Firmware version: " + str(cs.getVersion()))
print("Sensor status:    " + str(hex(cs.getStatus())))
print("Rain counter:     " + str(cs.getRainCount()))
print("Wind average:     " + str(round(cs.getWindAvg(), 2)))
print(" -> Raw:          " + str(cs.getWindAvgRaw()))
print("Wind maximum:     " + str(round(cs.getWindMax(), 2)))
print(" -> Raw:          " + str(cs.getWindMaxRaw()))
print("Light average:    " + str(cs.getLightAvg()))