import requests 
import time
import sys
sys.path.append('../')
import rgb1602
import datetime

def todayAt (hr, min=0, sec=0, micros=0):
   now = datetime.datetime.now()
   return now.replace(hour=hr, minute=min, second=sec, microsecond=micros)

timeNow = datetime.datetime.now()

# Set Data URL
url = 'http://admin:KQYT8RBX@192.168.0.35/inverter.cgi'

# Set up LCD Colour
colorR = 204
colorG = 31
colorB = 230
lcd=rgb1602.RGB1602(16,2)
lcd.setRGB(colorR, colorG, colorB)

# Only pull data during daylight hours.
while timeNow < todayAt (18):
#	lcd.noDisplay()
	lcd.clear()

	# Making a get request
	

	response = None
  
	while response is None:
		try:
			response = requests.get(url)
		except requests.HTTPError as e:
			print(f"[!] Exception caught: {e}")

	varlst = response.text.split(';') 
	power =  varlst[4]
	total = varlst[5]

	# Print a message to the LCD.
	lcd.setCursor(0,0)
	power = int(power) /1000
	total = int(total) /10
	lcd.printout("Power: " + str(power) + " KW")
	lcd.setCursor(0,1)
	lcd.printout("Total: " + str(total) + " KW")

	#time.sleep(1)
	#i = 0

	time.sleep(30)
	timeNow = datetime.datetime.now()
lcd.noDisplay()
lcd.setRGB(0,0,0)


