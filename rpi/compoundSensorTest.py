from pprint import pprint
from compoundSensor import compoundSensor

# Compound sensor object, baseline wind value of 67.
cs = compoundSensor(67)

print("Firmware version: " + str(cs.getVersion()))
print("Sensor status:    " + str(cs.getStatus()))
print("Rain counter:     " + str(cs.getRainCount()))
print("Wind average:     " + str(round(cs.getWindAvg(), 2)))
print("Wind maximum:     " + str(round(cs.getWindMax(), 2)))
print("Light average:    " + str(cs.getLightAvg()))