from Lane import Lane
import time
import json

class Bridge(object):
	def __init__(self):
		self.timer = 0
		self.bridgeopened = False
		self.bridgeopen = False
		self.allboatspassed = False
		self.lanes = [Lane("1.13"),Lane("4.1"),Lane("4.2")]
		self.lanes[0].trafficlightstatus = "green"

	def ManageBridge(self, c):
		if (self.bridgeopen == self.bridgeopened):
			if self.timer > 0 or self.allboatspassed:
				if (time.time() - self.timer) > 25 or self.allboatspassed:
					self.bridgeopen = not self.bridgeopen
					self.SendBridgeData(c)
					self.timer = 0
					self.allboatspassed = False
			elif (not self.bridgeopened):
				for lane in self.lanes:
					if lane.id.find("4.") == 0 and lane.triggered:
						self.timer = time.time()
			elif (self.bridgeopened):
				self.allboatspassed = True
				for lane in self.lanes:
					if lane.id.find("4.") == 0 and lane.triggered:
						self.allboatspassed = False
						break

	def SendBridgeData(self, c):
		c.send(json.dumps({'type':'BridgeData','bridgeOpen':self.bridgeopen})+'\n')