#!/usr/bin/python 

# smll.pi-0.1.0
# smll client for raspberry pi


import RPi.GPIO as GPIO
import sys
import time
import subprocess
import logging
import datetime as dt

# logging.basicConfig(filename='main.py.log',level=logging.DEBUG)
last_ctx_updated = dt.datetime.now() 
ctx_interval = 5 
play_index = 0

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

	sys.stdout.write('*')

	if (now-last_ctx_updated).seconds > ctx_interval :
		logging.info("it's time for context update")
		res = subprocess.call("wget -nc http://smll.herokuapp.com/device/serial/ctx", shell=True)
		if res == 0 :
			print "ctx update completed"
			last_ctx_updated = now
			play_index = 0
			file_download()
		else :
			print "ctx update failed"
			time.sleep(1) #wait before checking again if nothing detected

def file_download() :
	lines = tuple(open("./ctx", 'r'))	
	for line in lines:
		res = subprocess.call("wget -nc http://smll.herokuapp.com/speech/9/"+line, shell=True)

def process() :
	logging.info("process")
	ctx_update()

def play() :
	global play_index

	lines = tuple(open("./ctx", 'r'))	
	res = subprocess.call("mpg123 " + lines[play_index], shell=True)

	if play_index >= len(lines) :
		play_index = 0
	

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
