from Lane import Lane
import time
import json

class Bridge(object):
	def __init__(self):
		self.timer = 0
		self.bridgeopened = False
		self.bridgeopen = False
		self.allboatspassed = False
		self.resseted = False
		self.carlanes = [Lane("1.13")]
		self.boatlanes = [Lane("4.1"),Lane("4.2")]
		self.carlanes[0].trafficlightstatus = "green"

	def ManageBridge(self, c):
		if (self.bridgeopen == self.bridgeopened):
			if self.bridgeopen:
				return self.brideopen, self.bridgeopened, BridgeOpenRoutine(c)
			elif not bridgeopen:
				return return self.brideopen, self.bridgeopened, BridgeClosedRoutine(c)
		return self.bridgeopen, self.bridgeopened, []

	def BridgeClosedRoutine(self,c):
		if carlanes[0].trafficlightstatus == "red":
			carlanes[0].trafficlightstatus = "green"
			c.send(TrafficlightToJSON(carlanes))
		else: 
			for boat in boatlanes: 
				if boat.triggered > 0:
					carlanes[0].trafficlightstatus = "red"
					self.bridgeopen = not self.bridgeopen
					self.SendBridgeData(c)
					c.send(TrafficlightToJSON(carlanes))
		return carlanes

	def BridgeOpenRoutine(self,c):
		self.allboatspassed = True
		newsetboats = []
		for boat in self.boatlanes:
			if boat.triggered > 0:
				self.allboatspassed = False
				break
		if self.allboatspassed and time.time() - self.timer > 2:
			self.bridgeopened = not self.bridgeopened
			self.SendBridgeData(c)
			self.timer = time.time()
			for boat in boatlanes:
				if boat.trafficlightstatus == "green":
					boat.trafficlightstatus = "red"
					newsetboats.append(boat)
			c.send(TrafficlightToJSON(newsetboats))
		elif not self.allboatspassed and not self.resseted:
			for boat in boatlanes: 
				if boat.trafficlightstatus == "green" and boat.triggered == 0:
					boat.trafficlightstatus = "red"
					newsetboats.append(boat)
					c.send(TrafficlightToJSON(boat))
					self.timer = time.time()
					self.resseted = True
		elif not self.allboatspassed and time.time() - self.timer > 2 and self.resseted:
			for boat in boatlanes:
				if boat.triggered > 0:
					boat.trafficlightstatus = "green"
					newsetboats.append(boat)
					c.send(TrafficlightToJSON(boat))
					self.resseted = False
					break
		return newsetboats

	def SendBridgeData(self, c):
		c.send(json.dumps({'type':'BridgeData','bridgeOpen':self.bridgeopen})+'\n')

def TrafficlightToJSON(trafficinput):
	output = TrafficSendData()
	for x in trafficinput:
		newtrafficlightstatus = TrafficLight(x.id, x.trafficlightstatus)
		output.trafficLights.append(newtrafficlightstatus)
	return json.dumps(output, default=jdefault) + '\n'