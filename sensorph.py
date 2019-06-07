import string

import pylibftdi
from pylibftdi.device import Device
from pylibftdi.driver import FtdiError
from pylibftdi import Driver
import os
import time


class AtlasDevice(Device):

	def __init__(self, sn):
		Device.__init__(self, mode='t', device_id=sn)


	def read_line(self, size=0):
		"""
		taken from the ftdi library and modified to 
		use the ezo line separator "\r"
		"""
		lsl = len('\r')
		line_buffer = []
		while True:
			next_char = self.read(1)
			if next_char == '' or (size > 0 and len(line_buffer) > size):
				break
			line_buffer.append(next_char)
			if (len(line_buffer) >= lsl and
					line_buffer[-lsl:] == list('\r')):
				break
		return ''.join(line_buffer)

	def read_lines(self):
		"""
		also taken from ftdi lib to work with modified readline function
		"""
		lines = []
		try:
			while True:
				line = self.read_line()
				if not line:
					break
					self.flush_input()
				lines.append(line)
			return lines

		except FtdiError:
			print "Failed to read from the sensor."
			return ''

	def send_cmd(self, cmd):
		"""
		Send command to the Atlas Sensor.
		Before sending, add Carriage Return at the end of the command.
		:param cmd:
		:return:
		"""
		buf = cmd + "\r"     	# add carriage return
		try:
			self.write(buf)
			return True
		except FtdiError:
			print "Failed to send command to the sensor."
			return False


def get_ftdi_device_list():
	"""
	return a list of lines, each a colon-separated
	vendor:product:serial summary of detected devices
	"""
	dev_list = []

	for device in Driver().list_devices():
		# list_devices returns bytes rather than strings
		dev_info = map(lambda x: x.decode('latin1'), device)
		# device must always be this triple
		vendor, product, serial = dev_info
		dev_list.append(serial)
	return dev_list


def get_ph_reading():

	devices = get_ftdi_device_list()
	cnt_all = len(devices)

	if (cnt_all == 0):
		return 'Error: no device'

	try:
		dev = AtlasDevice(devices[0])
	except pylibftdi.FtdiError as e:
		return 'Error: ' + str(e)

	time.sleep(1)
	dev.flush()

	dev.send_cmd("C,0") # turn off continuous mode
	#clear all previous data
	time.sleep(1)
	dev.flush()

	c = 0

	while True:

		dev.send_cmd("R")
		lines = dev.read_lines()

		for i in range(len(lines)):
			if lines[i][0] != '*':
				line = lines[i]
				return 'Reading: ' + line

		c = c + 1
		if (c >= 45):
			break

		time.sleep(1)


	return 'Error: no reading'


readingph = get_ph_reading()

#file-output.py
f = open('ph_result.txt','w')
f.write(readingph)
f.close()
