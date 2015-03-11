# Fake packets

# Fan on, rain count
#Rain CPM: 510, Wind Avg: 77, Wind Max: 85, Light Avg: 21
#bytearray([0x0, 0x1, 0xE, 0x0, 0x0, 0x1, 0xFE, 0x0, 0x4D, 0x0, 0x55, 0x15])



###########
# Imports #
###########

import quick2wire.i2c as qI2c
import time

from pprint import pprint


#################
# cprMath class #
#################

class compoundSensor():
	"""
	compoundSensor is a class that supports I2C/SMBus communication with the compound weather sensor. The sonstructor accepts one optional argument - the I2C address of the compound weather sensor.
	"""

	def __init__(self, windOffset, cmpdAddr = 0x64):
		# I2C set up class-wide I2C bus
		self.__i2c = qI2c
		self.__i2cMaster = qI2c.I2CMaster()
		
		# Sensor's I2C address
		self.__cmpdAddr = cmpdAddr
		
		# Wind offset
		self.__windOffset = windOffset
		
		# Hold last recieved sample data.
		self.__lastData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		
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

	def __valMap(self, subject, subjectMin, subjectMax, targetMin, targetMax):
		"""
		__valMap(subject, subjectMin, subjectMax, targetMin, targetMax)
		
		Maps values from variable subject with a min and max, to a target range between min and max. This is a port of the Arduino map() function.
		See: http://arduino.cc/en/reference/map
		"""
		
		return (subject - subjectMin) * (targetMax - targetMin) / (subjectMax - subjectMin) + targetMin

	def __windScale2Speed(self, windVal):
		"""
		__windScale2Speed(windVal)
		
		Converts A/D converter wind reading to speed in KM/H.
		"""
		
		windSpeed = -1
		
		# Implement a floor since the ADC wanders a bit.
		if windVal < self.__windOffset:
			windVal = self.__windOffset
		
		# Drop value by offset
		windVal = windVal - self.__windOffset
		
		# Convert ADC readings to a wind speed in meters per second.
		windSpeed = self.__valMap(windVal, 0.0, 328.0, 0.0, 32.0)
		
		# Convert wind speed from meters/sec to km/h (1 m/S = 3.6 km/h)
		windSpeed = windSpeed * 3.6
		
		return windSpeed

	def __readRange(self, firstReg, lastReg):
		"""
		__readRange()
		
		Read a sequence of specified registers from the weather sensor. Returns a byte array.
		"""
		
		data = bytearray()
		
		# Boundary and sanity check to make sure we're looking for a valid range from low to high position
		if (firstReg >= 0) and (firstReg < (self.i2cRegSize - 1)) and (lastReg >= 1) and (lastReg < self.i2cRegSize) and (firstReg < lastReg):
			try:
				# Load the fake data frame.
				#fakeFrame = bytearray([0x0, 0x1, 0xE, 0x0, 0x0, 0x1, 0xFE, 0x0, 0x4D, 0x0, 0x55, 0x15])
				
				# Loop through specified registers
				for i in range(firstReg, lastReg + 1):
					#data.append(self.__i2c.read_byte_data(self.__cmpdAddr, i))
					#data.append(fakeFrame[i])
					res = self.__i2cMaster.transaction(self.__i2c.writing_bytes(self.__cmpdAddr, i), self.__i2c.reading(self.__cmpdAddr, 1))
					data.append(int(res[0]))
			except IOError:
				print("compoundSensor IO Error: Failed to read compound weather sensor on I2C bus.")
		
		pprint(data)
		
		return data
	
	def __readReg(self, register):
		"""
		__readReg(register)
		
		Read a specified register from the weather sensor. Returns a byte array..
		"""
		
		# Use a byte array for consistency with readRange()
		data = []
		
		# Load fake data frame.
		#fakeFrame = bytearray([0x0, 0x1, 0xE, 0x0, 0x0, 0x1, 0xFE, 0x0, 0x4D, 0x0, 0x55, 0x15])
		
		if(register >= 0) and (register < self.i2cRegSize):
			try:
				# Read the specific register.
				res = self.__i2cMaster.transaction(self.__i2c.writing_bytes(self.__cmpdAddr, register), self.__i2c.reading(self.__cmpdAddr, 1))
				data.append(res[0])
				#data.append(fakeFrame[register])
			
			except IOError:
				print("compoundSensor IO Error: Failed to read compound weather sensor on I2C bus.")
		
		return bytearray(data);

	def __readAll(self):
		"""
		__readAll()
		
		Get all registers from the compound sensor module. Returns a byte array containg 12 bytes.
		"""
		
		# Read all the bytes.
		return self.__readRange(self.i2c_fwMajor, self.i2c_lightAvg)
	
	def pollAll(self):
		"""
		pollAll()
		
		Poll all registers, and store the rast recieved value in our global __lastData array.
		"""
		
		# Read all registers, and set global lastData array.
		self.__lastData = self.__readAll()	

	def checkStatusReg(self, status):
		"""
		checkStatusReg(status)
		
		Checks the status register to see if given status[es] bit(s) are set. Returns true or false.
		"""
		
		retVal = False
		
		# See if the status bits we set are in fact all set.
		if int(self.__lastData[self.i2c_status] & status) == status:
			retVal = True
		
		return retVal

	def getStatus(self):
		"""
		getStatus()
		
		Get status byte. Returns a byte array.
		"""
		
		# Return the status byte.
		return self.__lastData[self.i2c_status]

	def getVersion(self):
		"""
		getVersion()
		
		Get the sensor's firmware version. Returns a version number as major.minor
		"""
		
		# Figure out the firmware version using the major and minor versions.
		return self.__lastData[self.i2c_fwMajor] + self.__lastData[self.i2c_fwMinor] / 10.0
	
	def getRainCount(self):
		"""
		Get the rain counter value. Returns a 32 bit unsigned integer.
		"""
		
		# Make sure we have stable output.
		if ~self.checkStatusReg(self.i2cStatus_data):
			time.sleep(.1)
			self.pollAll()
		
		# Put together a 32-bit unsigned integer representing the rain counter.
		rainCount = (self.__lastData[self.i2c_rainMSB] << 24) | (self.__lastData[self.i2c_rain2SB] << 16) | \
			(self.__lastData[self.i2c_rain3SB] << 8) | self.__lastData[self.i2c_rainLSB]
		
		return rainCount

	def getWindAvg(self):
		"""
		readWindAvg()
		
		Get average wind speed data registers from the compound sensor module. Returns wind speed in kph, rounded to two decimal places.
		"""
		
		# Make sure we have stable output.
		if ~self.checkStatusReg(self.i2cStatus_data):
			time.sleep(.1)
			self.pollAll()
		
		# Grab the average for the wind data and convert it to an int
		windAvgReading = (self.__lastData[self.i2c_windAvgMSB] << 8) | self.__lastData[self.i2c_windAvgLSB]
		
		# Convert the wind reading to a value in KPH
		windSpeed = self.__windScale2Speed(windAvgReading)
		
		# Return rounded windspeed.
		return round(windSpeed, 2)
	
	def getWindMax(self):
		"""
		readWindMax()
		
		Get max wind speed data registers from the compound sensor module. Returns wind speed in kph, rounded to two decimal places.
		"""
		
		# Make sure we have stable output.
		if ~self.checkStatusReg(self.i2cStatus_data):
			time.sleep(.1)
			self.pollAll()
		
		# Grab the average for the wind data and convert it to an int
		windMaxReading = (self.__lastData[self.i2c_windMaxMSB] << 8) | self.__lastData[self.i2c_windMaxLSB]
		
		# Convert the wind reading to a value in KPH
		windSpeed = self.__windScale2Speed(windMaxReading)
		
		# Return rounded windspeed.
		return round(windSpeed, 2)
	
	def getWindAvgRaw(self):
		"""
		readWindAvgRaw()
		
		Get average wind speed data registers from the compound sensor module. Returns the integer value of the register's MSB and LSB added together.
		"""
		
		# Make sure we have stable output.
		if ~self.checkStatusReg(self.i2cStatus_data):
			time.sleep(.1)
			self.pollAll()
		
		# Grab the average for the wind data and convert it to an int
		windAvgRaw = (self.__lastData[self.i2c_windAvgMSB] << 8) | self.__lastData[self.i2c_windAvgLSB]
		
		return int(windAvgRaw)
	
	def getWindMaxRaw(self):
		"""
		readWindMax()
		
		Get max wind speed data registers from the compound sensor module. Returns the integer value of the register's MSB and LSB added together.
		"""
		
		# Make sure we have stable output.
		if ~self.checkStatusReg(self.i2cStatus_data):
			time.sleep(.1)
			self.pollAll()
		
		# Grab the average for the wind data and convert it to an int
		windMaxRaw = (self.__lastData[self.i2c_windMaxMSB] << 8) | self.__lastData[self.i2c_windMaxLSB]
		
		return int(windMaxRaw)
	
	def getLightAvg(self):
		"""
		getLightAvg()
		
		Get the average amount of ambient light detected. Returns an integer between 0 and 255.
		"""
		
		# Make sure we have stable output.
		if ~self.checkStatusReg(self.i2cStatus_data):
			time.sleep(.1)
			self.pollAll()
		
		# Grab average light data
		lightAvgRaw = self.__lastData[self.i2c_lightAvg]
		
		return lightAvgRaw
