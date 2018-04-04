class Lane(object):
	def __init__(self, id, dependedlanes = []):
		self.trafficlightstatus = "red"
		self.dependedlanes = dependedlanes
		self.triggered = 0
		self.id = id
