class TrafficStuff(object):
	def __init__(self):
		self.type = "TrafficLightData"
		self.trafficLights = [trafficLight(1.1), trafficLight(1.2)]    

class trafficLight(object):
	def __init__(self, id, lightStatus="red"):
		self.id = id
		self.lightStatus = lightStatus