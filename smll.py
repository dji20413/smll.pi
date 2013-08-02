#!/usr/bin/python 

# smll.pi-0.1.0
# smll client for raspberry pi

import os 
import sys
import RPi.GPIO as GPIO
import sys
import time
import subprocess
import logging
import datetime as dt

# logging.basicConfig(filename='main.py.log',level=logging.DEBUG)
last_ctx_updated = 0 
ctx_interval = 60 
track = 0

def print_no_endl(str) :
	sys.stdout.write(str)
	sys.stdout.flush()

def gpio_initialize() :
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(11, GPIO.IN)

def ctx_update() :

	global last_ctx_updated
	global ctx_interval 

	now = dt.datetime.now()

	elapsed = 0
	if last_ctx_updated != 0 :
		elapsed = (now-last_ctx_updated).seconds 
		print "elapsed: %(el)d" % {'el' : elapsed}
	else :
		print "First context update" 

	if elapsed > ctx_interval or last_ctx_updated == 0 :
		logging.info("it's time for context update")
		res = subprocess.call("rm ctx", shell=True)
		res = subprocess.call("wget -nc http://smll.herokuapp.com/device/serial/ctx", shell=True)

		#if os.path.isfile("ctx") :
	  #	t_new = time.ctime(os.path.getctime("ctx"))

		#if os.path.isfile("ctx.now") :
			#t_now = time.ctime(os.path.getctime("ctx.now"))

		#if t_now != t_new  :
		#print "ctx update"
		#print "copy ctx -> ctx.now"
		#subprocess.call("cp -f ctx ctx.now", shell=True)
		track = 0
		file_download()
		#else :
		#	print "no ctx update"
		#	time.sleep(1) #wait before checking again if nothing detected

		# update last updated time
		last_ctx_updated = now 

def file_download() :
	lines = tuple(open("./ctx", 'r'))	
	for line in lines:
		res = subprocess.call("wget -nc http://smll.herokuapp.com/speech/9/"+line, shell=True)

def process() :
	logging.info("process")
	ctx_update()

def play() :
	global track 

	lines = tuple(open("./ctx", 'r'))	

	# track reset
	if track >= len(lines) :
		track = 0
	else :
		track = track + 1 
	
	res = subprocess.call("mpg123 " + lines[track], shell=True)

def main() :

	gpio_initialize()
	logging.info("main.py - smll python client")

	# main loop
	try:
		# loop to check PIR state/trigger a tweet (exit using Ctrl+C)
		while True:
			ir_val = GPIO.input(11)

			if not ir_val:
				# not active
				print_no_endl('-')
				process()
				time.sleep(0.5) #wait before checking again if nothing detected
			elif ir_val:
				print_no_endl('*')
				play()
				# wait until not active
				while ir_val:
					ir_val = GPIO.input(11)
					print_no_endl('+')
					process()
					time.sleep(0.5) #wait for sensor to reset/movement to stop before checking again

	except KeyboardInterrupt :
		print "Exit",
		sys.exit()

if __name__ == '__main__':
	main()
