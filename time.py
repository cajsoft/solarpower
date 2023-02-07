import datetime
def todayAt (hr, min=0, sec=0, micros=0):
   now = datetime.datetime.now()
   return now.replace(hour=hr, minute=min, second=sec, microsecond=micros)   

timeNow = datetime.datetime.now()
if timeNow < todayAt (16):
	print ('Too Early')
