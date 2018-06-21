from Lane import Lane
from TrafficLight import *
import time
import json

#The bridge and other lanes and boats that are influenced by the bridge. 
class Bridge(object):
	def __init__(self):
		self.timer = 0
		self.statetimer = 0
		self.bridgeopened = False
		self.bridgeopen = False
		self.changestate = False
		self.carlanes = [Lane("1.13")]
		self.boatlanes = [Lane("4.1"),Lane("4.2")]
		self.currentlane = None
		self.carlanes[0].trafficlightstatus = "green"

	#Main loop
	def manageBridge(self, socket):
		if (self.bridgeopen == self.bridgeopened):
			if self.bridgeopen:
				return self.bridgeopen, self.bridgeopened, self.bridgeOpenRoutine(socket)
			elif not self.bridgeopen:
				return self.bridgeopen, self.bridgeopened, self.bridgeClosedRoutine(socket)
		return self.bridgeopen, self.bridgeopened, []

	#Routine when the bridge is closed
	def bridgeClosedRoutine(self,socket):
		newsetlane = []
		if not self.changestate and not self.areAllBoatsPassed() and time.time() - self.statetimer > 20:
			if self.carlanes[0].trafficlightstatus == "green":
				self.carlanes[0].trafficlightstatus = "red"
			self.timer = time.time()
			newsetlane = self.carlanes
			self.changestate = True
		elif self.changestate and time.time() - self.timer > 4:
			self.bridgeopen = not self.bridgeopen
			self.sendBridgeData(socket)
			self.statetimer = time.time()
			self.changestate = False
		elif not self.changestate and self.carlanes[0].trafficlightstatus == "red":
			self.carlanes[0].trafficlightstatus = "green"
			newsetlane = self.carlanes
		if len(newsetlane) > 0:
			socket.send(TrafficLightData(newsetlane).classToJSON())
		return newsetlane

	#Routine when the bridge is open
	def bridgeOpenRoutine(self,socket):
		newsetboats = []
		if (self.areAllBoatsPassed() or time.time() - self.statetimer > 20) and time.time() - self.timer > 3 and (self.currentlane == None or self.currentlane.trafficlightstatus == "red"):
			self.bridgeopen = not self.bridgeopen
			self.statetimer = time.time()
			self.sendBridgeData(socket)
			self.currentlane = None
		elif time.time() - self.timer > 7 and self.currentlane != None and self.currentlane.trafficlightstatus == "green" and self.currentlane.triggered == 0:
			self.timer = time.time()
			self.currentlane.trafficlightstatus = "red"
			newsetboats.append(self.currentlane)
		elif time.time() - self.timer > 3 and (self.currentlane == None or self.currentlane.trafficlightstatus == "red"):
			if (self.currentlane == None or self.currentlane == self.boatlanes[0]) and self.boatlanes[1].triggered:
				self.currentlane = self.boatlanes[1]
			elif (self.currentlane == None or self.currentlane == self.boatlanes[1]) and self.boatlanes[0].triggered:
				self.currentlane = self.boatlanes[0]
			self.currentlane.trafficlightstatus = "green"
			newsetboats.append(self.currentlane)
			self.timer = time.time()
		if len(newsetboats) > 0:
			socket.send(TrafficLightData(newsetboats).classToJSON())
		return newsetboats

	#Sends request to open or close the bridge
	def sendBridgeData(self, socket):
		socket.send(json.dumps({'type':'BridgeData','bridgeOpen':self.bridgeopen})+'\n')

	#Checks if all the boats are passed
	def areAllBoatsPassed(self):
		for boat in self.boatlanes:
			if boat.triggered > 0:
				return False
		return True