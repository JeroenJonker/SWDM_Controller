from Lane import Lane
from TrafficLight import *
import time
import json

class Bridge(object):
	def __init__(self):
		self.timer = 0
		self.bridgeopened = False
		self.bridgeopen = False
		self.carlanes = [Lane("1.13")]
		self.boatlanes = [Lane("4.1"),Lane("4.2")]
		self.currentlane = None
		self.carlanes[0].trafficlightstatus = "green"

	def ManageBridge(self, c):
		if (self.bridgeopen == self.bridgeopened):
			if self.bridgeopen:
				return self.bridgeopen, self.bridgeopened, self.BridgeOpenRoutine(c)
			elif not self.bridgeopen:
				return self.bridgeopen, self.bridgeopened, self.BridgeClosedRoutine(c)
		return self.bridgeopen, self.bridgeopened, []

	def BridgeClosedRoutine(self,c):
		if self.carlanes[0].trafficlightstatus == "red":
			self.carlanes[0].trafficlightstatus = "green"
			c.send(TrafficlightToJSON(self.carlanes))
		else: 
			for boat in self.boatlanes: 
				if boat.triggered > 0:
					self.carlanes[0].trafficlightstatus = "red"
					self.bridgeopen = not self.bridgeopen
					self.SendBridgeData(c)
					c.send(TrafficlightToJSON(self.carlanes))
		return self.carlanes

	def BridgeOpenRoutine(self,c):
		newsetboats = []
		if self.AreAllBoatsPassed() and time.time() - self.timer > 4:
			self.bridgeopen = not self.bridgeopen
			self.SendBridgeData(c)
			self.currentlane.trafficlightstatus = "red"
			newsetboats.append(self.currentlane)
			self.currentlane = None
		elif time.time() - self.timer > 5 and not self.currentlane == None:
			if self.currentlane.triggered == 0:
				self.timer = time.time()
				self.currentlane.trafficlightstatus = "red"
				newsetboats.append(self.currentlane)
				self.currentlane = None
		elif self.currentlane == None and time.time() - self.timer > 4:
			for boat in self.boatlanes:
				if boat.triggered > 0:
					boat.trafficlightstatus = "green"
					newsetboats.append(boat)
					self.currentlane = boat
					self.timer = time.time()
					break
		if len(newsetboats) > 0:
			print str(TrafficlightToJSON(newsetboats))
			c.send(TrafficlightToJSON(newsetboats))
		return newsetboats

	def SendBridgeData(self, c):
		print "hello " + str(self.bridgeopen)
		c.send(json.dumps({'type':'BridgeData','bridgeOpen':self.bridgeopen})+'\n')

	def AreAllBoatsPassed(self):
		for boat in self.boatlanes:
			if boat.triggered > 0:
				return False
		return True

def TrafficlightToJSON(trafficinput):
	output = TrafficSendData()
	for x in trafficinput:
		newtrafficlightstatus = TrafficLight(x.id, x.trafficlightstatus)
		output.trafficLights.append(newtrafficlightstatus)
	return json.dumps(output, default=jdefault) + '\n'

def jdefault(o):
    if isinstance(o, set):
        return list(o)
    return o.__dict__