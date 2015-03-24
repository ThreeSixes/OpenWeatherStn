====================
Open Weather Station
====================

An open-source project to create local digital weather stations using various digital sensors, an Arduino, and a Raspberry Pi.

Features:
 - Temperature and humidity
 - Barometric pressure
 - Wind speed and direction
 - Rainfall severity
 - Ambient light levels
 - Easy-to-use web interface to retrieve weather data supporting JSON, REST, and a basic web page.

Sensors / sensing components:
- Anemometer (http://adafru.it/1733)
- AOSONG AM2315 Encased I2C Temperature/Humidity Sensor (http://adafru.it/1293)
- Parallax HMC5883L break out board (http://www.parallax.com/product/29133)
- Freescale MPL115A2 barometer (https://www.adafruit.com/products/992)
- Microchip MCP9808 High-accuracy thermometer (https://www.adafruit.com/products/1782)
- 2x Cadmimum Sulfide photocells (purchased from RadioShack)
- Red laser module (http://www.amazon.com/50mW-650nm-Focusable-Laser-Module/dp/B00S9JW26O/ref=sr_1_11?s=industrial&ie=UTF8&qid=1425583140&sr=1-11) 
- Funnel

Notes:
- Requires some soldering. Circuit diagrams will be added after the engineering and testing is complete.
- Sensors connected to Raspberry Pi using I2C and an I2C-safe level converter since most sensors used are 5V.
