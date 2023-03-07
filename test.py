
import requests
import json
import webbrowser
from datetime import datetime
from datetime import date


params = {"lat":55.614719, "lng":-4.498792, "date":date.today()}

def sunrisesunset(sun):
	f = r"https://api.sunrise-sunset.org/json?"
	a = requests.get(f, params=params)
	a = json.loads(a.text)
	a = a["results"]
	if sun == "Rise":
		sun = datetime.strptime(a["sunrise"], '%I:%M:%S %p')
	else:
		sun = datetime.strptime(a["sunset"], '%I:%M:%S %p')
	sun = sun.strftime('%H')
	return (sun)

b = sunrisesunset("Rise")
print(b)
