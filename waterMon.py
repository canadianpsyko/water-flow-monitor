#!/usr/bin/env python3

"""
Monitor a reed switch for water flow (Gallon per pulse) add each debounced event to an sqlite database.
Also have scheduling for a high flow valve with an <open> per <time> when enabled.
"""
import datetime
import time
import sqlite3

import schedule
import pigpio


def check_gpio_daemon():
	return true

def connect_db(db_filename):
	"""Connect to DB file"""
	conn = sqlite3.connect(db_filename)
	c = conn.cursor()
	return conn, c

def db_write():
	c.execute("INSERT INTO events VALUES (NULL, CURRENT_TIMESTAMP)")
	conn.commit()
	return None

		
def pi_callback(gpio, level, tick):
	"""
	event = time.time()
	global debounceTime
	global lastGood
	print("Event! at: ", event)
	if(debounceTime <= event - lastGood):
		db_write()
		print("added!")
		lastGood = event
		return None
	print("Too short, debounce")
	"""
	global event
	if event is None:
		event = time.time()
		print("Event!: ", event)

	
	

def off_list_gen(onList, onMinutes):
	wl = []
	for i in onList:
		wt = datetime.datetime.strptime(i, "%H:%M")
		wt = wt + datetime.timedelta(minutes = onMinutes)
		wl.append(wt.strftime("%H:%M"))
	return wl
	

def on_list_gen(startTime, endTime, outOfMinutes):
	startTime = datetime.datetime.strptime(startTime, "%H:%M")
	endTime = datetime.datetime.strptime(endTime, "%H:%M")
	if endTime <= startTime:
		print("nothing to do!")
		return []
	wl = []
	wt = startTime
	while wt < endTime:
		wl.append(wt.strftime('%H:%M'))
		wt = wt + datetime.timedelta(minutes = outOfMinutes)
	return wl

	
def db_export():
	out = c.execute("SELECT * FROM events")
	with open('./latest.csv', 'w', newline='') as file:
		for i in out:
			a = out.fetchone()
			csv.writer(file).writerow(a)



def setSchedule(onList, offList):
	for i in range(len(onList)):
		schedule.every().day.at(onList[i]).do(valve_on)
		schedule.every().day.at(offList[i]).do(valve_off)

def valve_on():
	global GPIORELAYPIN1
	thisPi.write(GPIORELAYPIN1, 1)
	


def valve_off():
	global GPIORELAYPIN1
	thisPi.write(GPIORELAYPIN1, 0)
	
	
	
	

#temp set constants
GPIORELAYPIN1 = 4
GPIORELAYPIN2 = 17
GPIORELAYPIN3 = 27
GPIORELAYPIN4 = 22
GPIOINPUTPIN = 16
ONMINUTES = 10
OUTOFMINUTES = 60
DBFILE = "watermon.sqlite"
#DBTABLE = "events"
#DBCOLUMN = "date_time"

lastGood = 0.0
debounceTime = 0.5
event = None
STARTTIME = '00:00'
ENDTIME = '06:00'


if __name__ == '__main__':
	#if check_gpio_daemon():
	#	print("Successfully connected to GPIO daemon!")
	#else:
	#	print("pigpiod is not running, please fix for any usefulness")
	#connect to DB
	conn, c = connect_db(DBFILE)
	#add read DB for settings
	#add check setting sanity
	thisPi = pigpio.pi()
	thisPi.set_mode(GPIOINPUTPIN, pigpio.INPUT)
	thisPi.set_pull_up_down(GPIOINPUTPIN, pigpio.PUD_UP)
	cb = thisPi.callback(GPIOINPUTPIN, pigpio.RISING_EDGE, pi_callback)
	thisPi.set_mode(GPIORELAYPIN1, pigpio.OUTPUT)
	#Create schedule list
	onList = on_list_gen(STARTTIME, ENDTIME, OUTOFMINUTES)
	offList = off_list_gen(onList, ONMINUTES)
	setSchedule(onList, offList)
	while 1:
		time.sleep(1)
		schedule.run_pending()
		if event is not None:
			db_write()
			event = None
			print("Event Written! at ", time.strftime("%H:%M:%S", time.localtime()))


	
	
