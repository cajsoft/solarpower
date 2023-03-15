import requests 
from datetime import datetime
from datetime import date
import datetime
from requests import HTTPError
from requests.exceptions import ConnectionError
import time
import signal
import sys
sys.path.append('../')
import rgb1602
import logging
import json
import webbrowser


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("/var/log/solarpower.log"),
                              logging.StreamHandler()])

def sunrisesunset(sun):
	# Set Location for Sunrise/Sunset

	params = {"lat":55.614719, "lng":-4.498792, "date":date.today()}

	f = r"https://api.sunrise-sunset.org/json?"
	try:
		a = requests.get(f, params=params)
		a = json.loads(a.text)
		a = a["results"]
		if sun == "Rise":
			sun = datetime.datetime.strptime(a["sunrise"], '%I:%M:%S %p')
		else:
			sun = datetime.datetime.strptime(a["sunset"], '%I:%M:%S %p')
		sun = sun.strftime('%H')
		return (int(sun))
	except requests.exceptions.HTTPError as err:
		return 0

def fiveminutesPassed(oldminute):
	currentminute = time.gmtime()[4]
	logging.debug("Current Minute: " + str(currentminute))
	logging.debug("Old Minute: " + str(oldminute))
	if (oldminute > 54) or (oldminute > currentminute):
		oldminute = 0
	if ((currentminute - oldminute) >= 5):
		return True
	else:
		if (oldminute > 54):
			oldminute = 0
		return False

def push_data(total,power):
	dateN = datetime.datetime.now()
	dateNow = dateN.strftime("%Y%m%d")
	timeNow = dateN.strftime("%H:%M")
	global lastrun
	if fiveminutesPassed(time.gmtime(lastrun)[4]):
		lastrun = time.time()
		try:
			response = requests.get("https://pvoutput.org/service/r2/addstatus.jsp?key=fc36eba378cf2c593fca85aa14549d00d3dd5132&sid=94488&d=" + str(dateNow) + 
			"&t=" + str(timeNow) + "&v1=" + total + "&v2=" + power)
			response.raise_for_status()
			logging.debug("Got response from pvoutput!")
		except requests.exceptions.HTTPError as err:
			logging.debug("Request to post FAILED!!")
		
		#raise SystemExit(err)

def put_ip_to_file(ipaddr):
	f = open('/home/pi/dfrobot/DFRobot_RGB1602_RaspberryPi/DFRobot_RGBLCD/python/solarip.txt', 'w')
	f.write(str(ipaddr)) 
	f.close()

def get_ip_from_file(): 
	ipaddr = open('/home/pi/dfrobot/DFRobot_RGB1602_RaspberryPi/DFRobot_RGBLCD/python/solarip.txt', 'r').read()
	ipaddr = ipaddr.replace('\n', '')
	logging.debug("I.P Address from file : " + ipaddr)
	return ipaddr

def signal_handler(signal, frame):
	lcd.noDisplay()
	lcd.setRGB(0,0,0)
	sys.exit(0)


def find_ip_of_logger(ipaddr):
	global url
	logging.debug("Increment ip address...") 
	if ipaddr > 253:
		ipaddr = 20
	else:
		ipaddr = ipaddr + 1
	url = 'http://admin:KQYT8RBX@192.168.0.' + str(ipaddr) + '/inverter.cgi'
	put_ip_to_file(ipaddr)
	return ipaddr




signal.signal(signal.SIGINT, signal_handler)

# Set Data URL
ipaddr = int(get_ip_from_file())
url = 'http://admin:KQYT8RBX@192.168.0.' + str(ipaddr) + '/inverter.cgi'

# Set up LCD Colour
colorR = 204
colorG = 31
colorB = 230

lastrun = time.time()

time.sleep(10)
lcd=rgb1602.RGB1602(16,2)

while True:
	timeN = datetime.datetime.now()
	timeNow = timeN.strftime("%H")
	#timeNow = timeNow.strftime("%H:%M:%S")
	logging.debug("Outside Loop - timeNow: " + str(timeNow) )
	#print("True")
	# Only pull data during daylight hours.
	while int(timeNow) > sunrisesunset("Rise") and int(timeNow) < sunrisesunset("Set"):	
		timeN = datetime.datetime.now()
		timeNow = timeN.strftime("%H")
		
		#ipaddr = get_ip_from_file()

		logging.debug("Inside Loop - > SunRise and SunSet")
    		#lcd.noDisplay()
		lcd.clear()
		# Making a get request
		response = None

		while True:
			logging.debug("Trying Connection to inverter...")
			try:
				response = requests.get(url,timeout=5)
				if response.status_code == 200:
					# Connection 200
					logging.debug('Got 200 Response!')
					break
				else:
					lcd.noDisplay()
					lcd.setRGB(0,0,0)
					logging.debug("Got " + str(response.status_code) + ", trying next host!")
					ipaddr = find_ip_of_logger(ipaddr)
					url = 'http://admin:KQYT8RBX@192.168.0.' + str(ipaddr) + '/inverter.cgi'
			except requests.ConnectionError as err:
				lcd.noDisplay()
				lcd.setRGB(0,0,0)
				logging.debug("Got Error trying next host!")
				ipaddr = find_ip_of_logger(ipaddr)
				url = 'http://admin:KQYT8RBX@192.168.0.' + str(ipaddr) + '/inverter.cgi'
				continue
		varlst = response.text.split(';') 
		power =  varlst[4]
		rawpower = power
		#print("power: " + power)
		logging.debug("Power - " + str(power))
		total = varlst[5]
		rawtotal = int(total) * 100
		#print("total: " + total)
		logging.debug("Total - " + str(total))
	        # Print a message to the LCD.
		#lcd.setRGB(colorR, colorG, colorB)
		#print("varlst:" + str(varlst))
		lcd.setCursor(0,0)
		if int(power) < 1000:
			lcd.setRGB(150,0,0)
			lcd.display()
			lcd.printout("Power: " + str(power) + " Watts")
		else:
			lcd.setRGB(0, 150,0)
			power = int(power) /1000
			lcd.display()
			lcd.printout("Power: " + str(power) + " KW")
		lcd.setCursor(0,1)
		if int(total) < 1:
			lcd.printout("Total: " + str(total) + " Watts")
		else:
			total = int(total) /10
			lcd.printout("Total: " + str(total) + " KW")
		#sleep 30 secs
		push_data(str(rawtotal), str(rawpower))
		time.sleep(60)
		timeN = datetime.datetime.now()
		timeNow = timeN.strftime("%H")
	lcd.noDisplay()
	lcd.setRGB(0,0,0)
	#sleep 10 mins
	time.sleep(1200)
#print("Not True")
logging.debug("End Prog")
lcd.noDisplay()
lcd.setRGB(0,0,0)
