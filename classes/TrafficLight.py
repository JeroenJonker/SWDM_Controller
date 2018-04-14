class TrafficSendData(object):
	def __init__(self):
		self.type = "TrafficLightData"
		self.trafficLights = []

class TrafficLight(object):
	def __init__(self, id, lightStatus="red"):
		self.id = id
		self.lightStatus = lightStatus