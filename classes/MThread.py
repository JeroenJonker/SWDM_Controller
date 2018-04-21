import threading
import json
from collections import namedtuple

class MThread(threading.Thread):
	def __init__(self, threadID, name, message, c, keep):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.message = message
		self.c = c
		self.keep = keep

	def run(self):
		print "Starting " + self.name
		while self.keep: 
			self.listening()
		print "exiting" + self.name

	def listening(self):
		received = self.c.recv(1024)
		print received
		if (len(received) > 0):
			#In python3 .decode('utf-8') / .encode('utf-8') nodig bij received
			newinfo = json.loads(received, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
			print newinfo
			self.message = newinfo

def getNewLanes(alltriggeredlanes):
	global currentlanes
	triggeredlanes = list(alltriggeredlanes)
	for triggerlane in triggeredlanes:
		if triggerlane in currentlanes:
			triggeredlanes.remove(triggerlane)
	return triggeredlanes