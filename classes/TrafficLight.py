import json

#Used for the message to the simulator
class TrafficLightData(object):
	def __init__(self, newdata):
		self.type = "TrafficLightData"
		self.trafficLights = self.addTrafficLights(newdata)

	#Returns all trafficlight in the data to the right TrafficLight format
	def addTrafficLights(self, newdata):
		trafficLights = []
		for x in newdata:
			newtrafficlightstatus = TrafficLight(x.id, x.trafficlightstatus)
			trafficLights.append(newtrafficlightstatus)
		return trafficLights

	#Returns the class as a JSON string
	def classToJSON(self):
		return json.dumps(self, default=self.JSONDefault) + '\n'

	#Makes sure the right types are compatable with the JSON format
	def JSONDefault(self, data):
	    if isinstance(data, set):
	        return list(data)
	    return data.__dict__

#Used for the message to the simulator
class TrafficLight(object):
	def __init__(self, id, lightStatus="red"):
		self.id = id
		self.lightStatus = lightStatus