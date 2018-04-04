class TrafficStuff(object):
	def __init__(self):
		self.type = "TrafficLightData"
		self.trafficLights = []

class trafficLight(object):
	def __init__(self, id, lightStatus="red"):
		self.id = id
		self.lightStatus = lightStatus