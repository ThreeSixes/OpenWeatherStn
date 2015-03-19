# mcp9808 class by ThreeSixes (https://github.com/ThreeSixes/py-mcp9808)
# This was originally part of the OpenWeatherStn project (https://github.com/ThreeSixes/OpenWeatherStn)

###########
# Imports #
###########

import quick2wire.i2c as qI2c
from pprint import pprint

##################
# hmc5883L class #
##################

class mcp9808:
    """
    mcp9808 is a class that supports communication with an I2C-connected Microchip MCP9808 thermometer. The constructor for this class accepts one argement:

    mcp9808Addr: The I2C address of the sensor, but will default to 0x18 if it's not specified.
    """

    # The themometer config variables are based on the MCP9808 datasheet
    # http://ww1.microchip.com/downloads/en/DeviceDoc/25095A.pdf

    def __init__(self, mcp9808Addr = 0x18):
        # I2C set up class-wide I2C bus
        self.__i2c = qI2c
        self.__i2cMaster = qI2c.I2CMaster()
        
        # Set global address var
        self.__addr = mcp9808Addr
        
        # Store the data we got from the last polling cycle
        self.__lastData = None
        
        # Confiuration registers
        self.regConfig = 0x01 # 16 bit registers...
        self.regTUpper = 0x02
        self.regTLower = 0x03
        self.regTCrit  = 0x04
        self.regTA     = 0x05
        self.regMfgID  = 0x06
        self.regDevID  = 0x07
        self.regRes    = 0x08 # 8 Bit register
        
        # Config register bits
        self.__regCfgHyst0  = 0x0400 # Temp hysterisis bit 0
        self.__regCfgHyst1  = 0x0200 # Temp hysterisis bit 1
        self.__regCfgShdn   = 0x0100 # Shutdown mode bit
        self.__regCfgCrtLck = 0x0080 # Critical temp lock bit
        self.__regCfgWinLck = 0x0040 # Temperature window lock bit
        self.__regCfgIntClr = 0x0020 # Interrupt clear bit
        self.__regCfgAlrtSt = 0x0010 # Alert output status bit
        self.__regCfgAlrtCt = 0x0008 # Alert output control bit
        self.__regCfgAlrtSl = 0x0004 # Alert output select bit
        self.__regCfgAlrtPl = 0x0002 # Alert output poliarity bit
        self.__regCfgAlrtMd = 0x0001 # Alert mode bit.
        
        # Temperature resolution bits
        self.__regResBit0   = 0x0002 # Temperature resolution bit 0
        self.__regResBit1   = 0x0001 # Temperature resolution bit 1
        
        # Temperature hysteresis settings
        self.tempHyst0      = 0x00 # Temperature hysterisis at 0 degrees. (Default)
        self.tempHyst1_5    = self.__regCfgHyst1 # 1.5 degrees C hysteresis
        self.tempHyst3_0    = self.__regCfgHyst0 # 3.0 degrees C hysteresis
        self.tempHyst6_0    = self.__regCfgHyst0 | self.__regCfgHyst1 # 6.0 degrees C hysteresis.
        
        # Mode settings
        self.modeContinuous = 0x00 # Continuous mode (default)
        self.modeShutdown   = self.__regCfgShdn # Single reading / shutdown or sleep mode
        
        # Critical temp lock
        self.lockCritTmp    = self.__regCfgCrtLck # Lock critical temp.
        
        # Lock temperature alert window
        self.lockTempWindow = self.__regCfgWinLck # Lock temperature window.
        
        # Interrupt clear bit
        self.clearInterrupt = self.__regCfgIntClr # Clear interrupt bit.
        
        # Alert output status bit
        self.alertStatus    = self.__regCfgAlrtSt # Alert status bit
        
        # Alert output control
        self.alertOutputOff = 0x00 # Disable alert output (default)
        self.alertOutputOn  = self.__regCfgAlrtCt # Enable alert output
        
        # Alert type selector
        self.alertSelAll    = 0x00 # Alert when the temperature leaves the window or exceeds crit. (default)
        self.alertSelCrit   = self.__regCfgAlrtSl # Only alert when the temp exceeds the critical temp.
        
        # Alert pin polarity
        self.alertPinLow    = 0x00 # Active-low alert pin. Requireds a pull up resistor. (default)
        self.alertPinHigh   = self.__regCfgAlrtPl # Active-high alert pin
        
        # Alert output mode
        self.alertModeComp  = 0x00 # Comparitor output mode (default)
        self.alertModeIntrr = self.__regCfgAlrtMd # Interrupt output mode.
        
        # Temperature resolution settings
        self.tempRes0_5     = 0x00 # 0.5 degrees C rsolution
        self.tempRes0_25    = self.__regResBit1 # 0.25 degrees C rsolution
        self.tempRes0_125   = self.__regResBit0 # 0.125 degrees C rsolution
        self.tempRes0_0625  = self.__regResBit0 | self.__regResBit1 # 0.0625 degrees C rsolution
        
        # Alert flags
        self.tempAlertCrit  = 0x8000 # Ambient temp vs. ciritcal temp.
        self.tempAlertUpper = 0x4000 # Ambient temp vs. upper temp.
        self.tempAlertLower = 0x2000 # Ambient temp vs. lower temp.
        self.tempAlertMask  = 0x1fff # Mask to remove temp flag bits from ambient temp value.
    
    def __readReg(self, register, byteCt):
        """
        __readReg(register, byteCt)
        
        Read a given register from the MCP9808 with a given byte length. Returns a bytearray of length specified by byteCt.
        """
        
        data = 0
        
        try:
            # Set the register we want to read.
            self.__i2cMaster.transaction(self.__i2c.writing_bytes(self.__addr, register))
            
            # Read the specific register.
            data = self.__i2cMaster.transaction(self.__i2c.reading(self.__addr, byteCt))
            data = bytearray(data[0])
            
        except IOError:
            raise IOError("mcp9808 IO Error: Failed to read MCP9808 sensor on I2C bus.")
            
        return data 
    
    def __writeReg(self, register, data):
        """
        __writeReg(register, data)
        
        Write data to a given register to the MCP9808. Data can be 1 to n bytes.
        """
        
        try:
            self.__i2cMaster.transaction(self.__i2c.writing_bytes(self.__addr, register, data))
        except IOError:
            raise IOError("mcp9808 IO Error: Failed to write to MCP9808 sensor on I2C bus.")
    
    def __getSigned(self, unsigned, bits = 11):
        """
        __getSigned(unsigned, [bits = 11])
        
        Converts an unsigned number to a two's compliment signed number.  Bits is the length of the number, and defaults to 11 if not specified.
        """
        
        # Placed holder for our signed number.
        signed = 0
        
        # If we have the sign bit set remove it and drop the numbe below the zero line.
        if (unsigned & (1 << (bits - 1))) != 0:
            signed = unsigned - (1 << bits)
        # If not, the nubmer is positive and we don't need to do anything.
        else:
            signed = unsigned
        
        return signed
    
    def __makeSigned(self, signed, bitCt = 11):
        """
        __makeSigned(signed, [bitCt = 11])
        
        Creates a signed integer. Requires one argument which is a signed temperature, and has an optional value which is the big length. Returns an unsigned inteter with lengh specified in bitCt.
        
        *** NOT YET IMPLEMENTED ***
        """
    
    def getReg(self, register):
        """
        getReg(register)
        
        Gets the value of a given register. Returns a byte array.
        """
        
        retVal = 0
        
        if register < 8:
            retVal = self.__readReg(register, 2)
        else:
            retVal = self.__readReg(register, 1)
        
        return retVal
    
    def setReg(self, register, value):
        """
        setReg(register, value)
        
        Manually set the value of a given register. The writable registers are 0x01 (CONFIG) through 0x04 (Critical Temp)
        """
        
        # Make sure we're trying to write to a R/W register
        if (register >= self.regConfig) and (register <= self.regTCrit):
            self.__writeReg(register, value)
        else:
            raise ValueError("MCP9808 register must be writable to set it.")
    
    def setConfig(self, config):
        """
        setConfig(config)
        
        Set the configuration to specified settings. See the data sheet and 
        """
        
        # Set the config register with the desired settings.
        self.setReg(self.regConfig, config)
    
    def setTempWindow(self, upperTemp, lowerTemp):
        """
        setTempWindow(upperTemp, lowerTemp)
        
        Set the temperature window for the sensor. If the temperature falls outside the values between upper and lower arguments the window alert bit is set.
        
        *** NOT YET IMPLEMENTED ***
        """
    
    def setTempCritical(self, critTemp):
        """
        setTempWindow(critTemp)
        
        Set the critical temperature for the sensor. If the temperature matches or exceeds the critical temperature specified the critical temperature alerm bit is set.
        
        *** NOT YET IMPLEMENTED ***
        """
    
    def getAmbientTemp(self):
        """
        getAmbientTemp()
        
        Get ambient temperature data. Returns a temperature in degress C., with up to four decimal points.
        """
        
        # Get the contents of the ambient temperature register.
        i2cRaw = self.getReg(self.regTA)
        
        # Get the temperature bytes, sans alert flags.
        tempBytes = (((i2cRaw[0] << 8) | i2cRaw[1]) & self.tempAlertMask)
        
        # Get our signed int from the incoming 13-byte integer.
        signedNum = self.__getSigned(tempBytes, 13)
        
        # LSB = 0.0625, so adjust the number in terms of the LSB.
        signedNum = signedNum * 0.0625
        
        return signedNum
    
    def checkAlarmFlags(self, flags, strict = False):
        """
        checkAlarmFlags(flags)
        
        Check for alarm flags. Accepts one mandatory and one optional argument. The mandatory argument is the flags we're checking for.
        The Strict flag is set when we want to ensure a flag or set of flags is set, and only the specified flags.
        
        Returns True or False.
        """
        
        retVal = False
        
        # Get the contents of the ambient temperature register.
        i2cRaw = self.getReg(self.regTA)
        
        # Get the temperature bytes, sans alert flags.
        tempBytes = (((i2cRaw[0] << 8) | i2cRaw[1]) & ~self.tempAlertMask)
        
        # See if we're running strict checks
        if strict:
            # Make sure we have precicely the flags we're looking for.
            if (tempBytes & flags) == flags:
                return True
        else:
            # If we're not in strict mode, just see if the specified flag is set.
            if (tempBytes & flags) > 0:
                return True
        
        return retVal