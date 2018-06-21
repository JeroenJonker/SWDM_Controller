import json

class TrafficLightData(object):
	def __init__(self, newdata):
		self.type = "TrafficLightData"
		self.trafficLights = self.AddTrafficLights(newdata)

	def AddTrafficLights(self, newdata):
		trafficLights = []
		for x in newdata:
			newtrafficlightstatus = TrafficLight(x.id, x.trafficlightstatus)
			trafficLights.append(newtrafficlightstatus)
		return trafficLights

	def ClassToJSON(self):
		return json.dumps(self, default=self.JSONDefault) + '\n'

	def JSONDefault(self, data):
	    if isinstance(data, set):
	        return list(data)
	    return data.__dict__

class TrafficLight(object):
	def __init__(self, id, lightStatus="red"):
		self.id = id
		self.lightStatus = lightStatus