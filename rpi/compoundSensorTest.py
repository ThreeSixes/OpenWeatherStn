from pprint import pprint
from compoundSensor import compoundSensor

# Compound sensor object, baseline wind value of 67.
cs = compoundSensor(67)

print(str(cs.getVersion()))
print(str(cs.getRainCount()))
pprint(cs.checkStatusReg(cs.i2cStatus_data))
print(str(cs.getWindAvg()))
print(str(cs.getWindMax()))