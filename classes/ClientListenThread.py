import socket
import json   
from classes.TrafficLight import TrafficLightData, TrafficLight
from classes.Bridge import Bridge
from classes.Intersection import Intersection
from classes.UI import UI
import threading
from time import sleep   
import time 
from collections import namedtuple

#Listens to client messages and updates the right parts
class ClientListenThread(threading.Thread):
	def __init__(self, socket, keep, bridgestatus, intersectionstatus, UI):
		threading.Thread.__init__(self)
		self.socket = socket
		self.keep = keep
		self.bridgestatus = bridgestatus
		self.intersectionstatus = intersectionstatus
		self.UI = UI

	#Main loop
	def run(self):
		print "Starting ClientListenThread"
		while self.keep: 
			self.listen()
		print "Exiting ClientListenThread"

	#Waits for client message to handle
	def listen(self):
		received = self.socket.recv(2048)
		if (len(received) > 0):
			received = (received).strip().lower()
			splittedmessage = received.split('\n')
			for message in splittedmessage:
				newinfo = json.loads(message, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
				self.update(newinfo)

	#Updates based on the type of message
	def update(self,updatedtrigger):
	 	# secondarytrigger type is not used
		if (updatedtrigger.type == "primarytrigger"):
			self.updateTriggerLanes(updatedtrigger)
		elif (updatedtrigger.type == "bridgestatusdata"):
			self.bridgestatus.bridgeopened = updatedtrigger.opened
			self.UI.updateBridgeStatus(self.bridgestatus.bridgeopen, self.bridgestatus.bridgeopened)
		elif (updatedtrigger.type == "timescaledata"):
			self.confirmTimescale(updatedtrigger)

	#Updates based on lane
	def updateTriggerLanes(self,updatedtrigger):
		if self.updateSpecificIntersectionLanes(updatedtrigger, self.intersectionstatus.carlanes): return
		if self.updateSpecificIntersectionLanes(updatedtrigger, self.intersectionstatus.bicyclelanes): return
		if self.updateSpecificBridgeLanes(updatedtrigger, self.bridgestatus.carlanes): return
		if self.updateSpecificBridgeLanes(updatedtrigger, self.bridgestatus.boatlanes): return
		if self.updateSpecificIntersectionLanes(updatedtrigger, self.intersectionstatus.pedestrianlanes): return

	#Updates bridgelanes
	def updateSpecificBridgeLanes(self,updatedtrigger,specificlanes):
		for lane in specificlanes:
			if updatedtrigger.id == lane.id:
				if (updatedtrigger.triggered):
					lane.triggered = 1
				else:
					lane.triggered = 0
				return True
		return False

	#Updates intersectionlanes
	def updateSpecificIntersectionLanes(self,updatedtrigger,specificlanes):
		for lane in specificlanes:
			if updatedtrigger.id == lane.id:
				if (updatedtrigger.triggered) and not lane in self.intersectionstatus.alltriggeredlanes:
					self.intersectionstatus.alltriggeredlanes.append(lane)
					lane.triggered += 1
				elif lane in self.intersectionstatus.alltriggeredlanes and lane in self.intersectionstatus.alltriggeredlanes:
					self.intersectionstatus.alltriggeredlanes.remove(lane)
					lane.triggered -= 1
				return True
		return False

	#Confirms timescale for simulator
	def confirmTimescale(self, updatedtrigger):
		global timescale 
		timescale = updatedtriggers.scale
		self.socket.send(json.dumps({'type':'TimeScaleVerifyData', 'status':False}) +'\n')