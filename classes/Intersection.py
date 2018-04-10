class Intersection(object):
	def __init__(self):
		self.currentlanes = []
		self.timer = 0
		self.primarytriggeredlanes = []
		self.secondarytriggeredlanes = []
		self.resseted = False

	def getTriggeredLanes(self):
		return (self.secondarytriggeredlanes + self.primarytriggeredlanes)

	def getNewTriggeredLanes(self):
		triggeredlanes = self.getTriggeredLanes()
		for triggerlane in triggeredlanes:
			if triggerlane in self.currentlanes:
				triggeredlanes.remove(triggerlane)
		return triggeredlanes