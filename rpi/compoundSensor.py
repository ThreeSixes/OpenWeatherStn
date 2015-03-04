# Fake packets

# Wind @ stop, min average observed: 66
# Rain CPM: 0, Wind Avg: 67, Wind Max: 68, Light Avg: 18
# bytearray([0x0, 0x1, 0xE, 0x0, 0x0, 0x0, 0x0, 0x0, 0x44, 0x0, 0x0, 0x12]) 

# Fan on, rain count
# Rain CPM: 5999, Wind Avg: 84, Wind Max: 90, Light Avg: 22
# bytearray([0x0, 0x1, 0xE, 0x0, 0x0, 0x17, 0x6F, 0x0, 0x5A, 0x0, 0x0, 0x16]) 


###########
# Imports #
###########

import smbus
from pprint import pprint


#################
# cprMath class #
#################

class compoundSensor():
	"""
	compoundSensor is a class that supports I2C/SMBus communication with the compound weather sensor. The sonstructor accepts one optional argument - the I2C address of the compound weather sensor.
	"""

	def __init__(self, windCal, cmpdAddr = 0x64):
		# I2C set up class-wide I2C bus
		self.i2c = smbus.SMBus(1)
	
		# Sensor's I2C address
		self.cmpdAddr = cmpdAddr
		
		### Register settings and definitions ###
		
		# Actual number of one-byte registers
		self.i2cRegSize    =      12
		
		# Register name -> location
		self.i2c_fwMajor =        0
		self.i2c_fwMinor =        1
		self.i2c_status  =        2
		self.i2c_rainMSB =        3
		self.i2c_rain2SB =        4
		self.i2c_rain3SB =        5
		self.i2c_rainLSB =        6
		self.i2c_windAvgMSB =     7
		self.i2c_windAvgLSB =     8
		self.i2c_windMaxMSB =     9
		self.i2c_windMaxLSB =     10
		self.i2c_lightAvg   =     11
		
		# Status register dictionary
		self.i2cStatus_initpoll = 0x01
		self.i2cStatus_data =     0x02
		self.i2cStatus_wind =     0x04
		self.i2cStatus_rain =     0x08
		self.i2cStatus_light =    0x10

	def valMap(self, subject, subjectMin, subjectMax, targetMin, targetMax):
		"""
		valMap(subject, subjectMin, subjectMax, targetMin, targetMax)
		
		Maps values from variable subject with a min and max, to a target range between min and max. This is a port of the Arduino map() function.
		See: http://arduino.cc/en/reference/map
		"""
		
		return (subject - subjectMin) * (targetMax - targetMin) / (subjectMax - subjectMin) + targetMin

	def readRange(self, firstReg, lastReg):
		"""
		readRange()
		
		Read a sequence of specified registers from the weather sensor. Returns a byte array.
		"""
		
		data = bytearray()
		
		# Boundary and sanity check to make sure we're looking for a valid range from low to high position
		if (firstReg >= 0) and (firstReg < (self.i2cRegSize - 1)) and (lasttReg >= 1) and (lastReg < self.i2cRegSize) and (firstReg > lastReg):
			try:
				# Keep track of the index
				n = 0
				
				
				
				# Loop through specified registers
				for i in range(firstReg, lastReg):
					#data[n] = self.i2c.read_byte_data(self.cmpAddr, i)
					fakeFrame = bytearray([0x0, 0x1, 0xE, 0x0, 0x0, 0x17, 0x6F, 0x0, 0x5A, 0x0, 0x0, 0x16])
					data[n] = fakeFrame[i]
					
					# Increment index
					n = n + 1
			
			except IOError:
				print "compoundSensor IO Error: Failed to read compound weather sensor on I2C bus."
		
		return data;
	
	
	def readReg(self, register):
		"""
		readReg(register)
		
		Read a specified register from the weather sensor. Returns a byte array..
		"""
		
		# Use a byte array for consistency with readRange()
		data = bytearray([0])
		
		if(register >= 0) and (register < self.i2cRegSize):
			try:
				# Read the specific register.
				#data[0] = self.i2c.read_byte_data(self.cmpAddr, register)
				fakeFrame = bytearray([0x0, 0x1, 0xE, 0x0, 0x0, 0x17, 0x6F, 0x0, 0x5A, 0x0, 0x0, 0x16])
				data[0] = fakeFrame[register]
			
			except IOError:
				print "compoundSensor IO Error: Failed to read compound weather sensor on I2C bus."
		
		return data;
		

	def readAll(self):
		"""
		getAll()
		
		Get all registers from the compound sensor module. Returns a byte array containg 12 bytes.
		"""
		
		# Read all the bytes.
		return readRange(self.i2c_fwMajor, self.i2c_lightAvg)
	
	def checkStatusReg(self, status):
		"""
		checkStatusReg(status)
		
		Checks the status register to see if a given status is set. Returns true or false.
		"""
		
		retVal = False
		
		statusByte = self.readReg(self.i2c_status)
		
		if (statusByte[0] & status) > 0:
			retVal = True
		
		return retVal

	def getVersion(self):
		"""
		getVersion()
		
		Get the sensor's firmware version. Returns a version number as major.minor
		"""
		
		verRaw = readRange(self.i2c_fwMajor, self.i2c_fwMinor)
		
		return verRaw[0] + (verRaw[1] / 10)
	
	def getRainCount(self):
		"""
		Get the rain counter value. Returns a 32 bit unsigned integer.
		"""
		
		rainRaw = self.readRange(self.i2c_rainMSB, self.i2c_rainLSB)
		rainCount = (rainRaw[0] << 24) | (rainRaw[1] << 16) | (rainRaw[2] << 8) | rainRaw[3]
		
		return rainCount
	
	def windScale2Speed(self, windVal):
		"""
		windScale2Speed(windVal)
		
		Converts A/D converter wind reading to speed in KM/H.
		"""
		
		windSpeed = -1
		
		# Convert ADC readings to a wind speed in meters per second.
		windSpeed = self.valMap(float(windVal), 0.0, 1023.0, 0.0, 32.0)
		
		# Convert wind speed from meters/sec to km/h (1 m/S = 3.6 km/h)
		windSpeed = windSpeed * 3.6
		
		return windSpeed

	def getWindAvg(self):
		"""
		readWindAvg()
		
		Get average wind speed data registers from the compound sensor module. Returns wind speed in kph.
		"""
		
		# Grab the average for the wind data and convert it to an int
		windAvgRaw = self.readRange(self.i2c_windAvgMSB, self.i2c_windAvgLSB)
		windAvgReading = (windAvgRaw[0] << 8) | windAvgRaw[1]
		
		# Convert the wind reading to a value in KPH
		windSpeed = self.windScale2Speed(windAvgReading)
		
		return windSpeed
	
	def getWindMax(self):
		"""
		readWindMax()
		
		Get max wind speed data registers from the compound sensor module. Returns wind speed in kph.
		"""
		
		# Grab the average for the wind data and convert it to an int
		windMaxRaw = self.readRange(self.i2c_windMaxMSB, self.i2c_windMaxLSB)
		windMaxReading = (windMaxRaw[0] << 8) | windMaxRaw[1]
		
		# Convert the wind reading to a value in KPH
		windSpeed = self.windScale2Speed(windMaxReading)
		
		return windSpeed
	
	def getLightAvg(self):
		"""
		getLightAvg()
		
		Get the average amount of ambient light detected. Returns an integer between 0 and 255.
		"""
		
		# Grab average light data
		lightAvgRaw = self.readReg(self.i2c_lightAvg)
		
		return lightAvgRaw[0]
	