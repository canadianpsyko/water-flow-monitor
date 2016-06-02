#!/usr/bin/env python3

"""
Monitor a reed switch for water flow (Gallon per pulse) add each debounced event to an sqlite database.
Also have scheduling for a high flow valve with an <open> per <time> when enabled.
"""
import atexit
import csv
import datetime
import sqlite3
import time

import pigpio
import schedule


def check_gpio_daemon():
	return true


def clean_exit():
	valve_off()
	thisPi.stop()
	print("See you later!")


def connect_db(db_filename):
	"""Connect to DB file"""
	conn = sqlite3.connect(db_filename)
	c = conn.cursor()
	return conn, c


def db_export():
	out = c.execute("SELECT * FROM events")
	with open('/home/pi/Desktop/latest.csv', 'w', newline='') as outfile:
		csv.writer(outfile).writerows(out)
	print("Output written, enjoy!")


def db_write():
	c.execute("INSERT INTO events VALUES (NULL, CURRENT_TIMESTAMP)")
	conn.commit()

	
def exit_message():
	print("Exited cleanly, see you later!")


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


def pi_callback(gpio, level, tick):
	global event
	if event is None:
		event = time.localtime()
		#print("Event!: ", event)

	

def setSchedule(onList, offList):
	for i in range(len(onList)):
		schedule.every().day.at(onList[i]).do(valve_on)
		schedule.every().day.at(offList[i]).do(valve_off)


def valve_off():
	global GPIORELAYPIN1
	thisPi.write(GPIORELAYPIN1, 0)


def valve_on():
	global GPIORELAYPIN1
	thisPi.write(GPIORELAYPIN1, 1)
	


#set constants
GPIORELAYPIN1 = 4
GPIORELAYPIN2 = 17
GPIORELAYPIN3 = 27
GPIORELAYPIN4 = 22
GPIOINPUTPIN = 16
DEBOUNCETIME = 300000
ONMINUTES = 10
OUTOFMINUTES = 60
STARTTIME = '00:00'
ENDTIME = '06:00'
DBFILE = "watermon.sqlite"
OUTPUTTIME = "07:00"
#DBTABLE = "events"
#DBCOLUMN = "date_time"
#lastGood = 0.0
event = None


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
	thisPi.set_glitch_filter(GPIOINPUTPIN, DEBOUNCETIME)
	cb = thisPi.callback(GPIOINPUTPIN, pigpio.RISING_EDGE, pi_callback)
	thisPi.set_mode(GPIORELAYPIN1, pigpio.OUTPUT)
	#ensure valve closed on start:
	valve_off()
	#Create schedule list
	onList = on_list_gen(STARTTIME, ENDTIME, OUTOFMINUTES)
	offList = off_list_gen(onList, ONMINUTES)
	setSchedule(onList, offList)
	#setup csv output
	schedule.every().day.at(OUTPUTTIME).do(db_export)
	#ensure valve is off at exit
	atexit.register(conn.close)
	atexit.register(clean_exit)
	while 1:
		time.sleep(1)
		schedule.run_pending()
		if event is not None:
			db_write()
			print("Event from: ", time.strftime("%H:%M:%S", event))
			print("Event Written! at ", time.strftime("%H:%M:%S", time.localtime()))
			event = None
