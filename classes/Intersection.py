from Lane import Lane
import time
from time import sleep
from TrafficLight import TrafficSendData, TrafficLight
import json


class Intersection(object):
    def __init__(self):
        self.currentlanes = []
        self.timer = 0
        self.alltriggeredlanes = []
        self.state = "red"
        self.carlanes = [Lane("1.1", ["1.5", "1.9","2.1","2.4","3.1.1","3.1.2","3.4.3","3.4.4"]), 
        				 Lane("1.2", ["1.5", "1.9", "1.10", "1.11", "1.12","2.1","2.3","3.1.1","3.1.2","3.3.3","3.3.4"]),
        				 Lane("1.3", ["1.5", "1.6", "1.7", "1.8", "1.9", "1.11", "1.12","2.1","2.2","3.1.1","3.1.2","3.2.3","3.2.4"]),
                         Lane("1.4", ["1.6", "1.8", "1.12","2.1","2.2","3.1.3","3.1.4","3.2.1","3.2.2"]),
                         Lane("1.5", ["1.1", "1.2", "1.3", "1.6", "1.8", "1.9", "1.10", "1.11", "1.12","2.2","2.3","2.4","3.2.1","3.2.2","3.3.3","3.3.4","3.4.3","3.4.4"]),
                         Lane("1.6", ["1.3", "1.4", "1.5", "1.7", "1.11"]),
                         Lane("1.7", ["1.3", "1.6", "1.11","2.2","2.3","3.2.3","3.2.4","3.3.1","3.3.2"]),
                         Lane("1.8", ["1.3", "1.4", "1.5", "1.11", "1.12", "2.1","2.3","3.1.3","3.1.4", "3.3.1","3.3.2"]),
                         Lane("1.9", ["1.1", "1.2", "1.3", "1.5", "1.11", "1.12", "2.3","2.4","3.3.1","3.3.2","3.4.3","3.4.4"]),
                         Lane("1.10", ["1.2", "1.5","2.3","2.4","3.3.3","3.3.4","3.4.1","3.4.2"]),
                         Lane("1.11", ["1.2", "1.3", "1.5", "1.6", "1.7", "1.8", "1.9", "2.2", "2.4", "3.2.3", "3.2.4", "3.4.1","3.4.2"]),
                         Lane("1.12", ["1.2", "1.3", "1.4", "1.5", "1.8", "1.9", "2.1", "2.4", "3.1.3", "3.1.4" , "3.4.1","3.4.2"])]
        self.bicyclelanes = [Lane("2.1", ["1.1", "1.2", "1.3", "1.4", "1.8", "1.12"]), Lane("2.2", ["1.3", "1.4", "1.5", "1.7", "1.11"]),
                             Lane("2.3", ["1.2", "1.5", "1.7", "1.8", "1.9", "1.10"]), Lane("2.4", ["1.1", "1.5", "1.9", "1.10", "1.11", "1.12"])]
        self.pedestrianlanes = [Lane("3.1.1", ["1.1", "1.2", "1.3"]), Lane("3.1.2", ["1.1", "1.2", "1.3"]), Lane("3.2.1", ["1.5", "1.4"]),
                                Lane("3.2.2", ["1.5", "1.4"]),
                                Lane("3.3.1", ["1.7", "1.8", "1.9"]), Lane("3.3.2", ["1.7", "1.8", "1.9"]), Lane("3.4.1", ["1.10", "1.11", "1.12"]),
                                Lane("3.4.2", ["1.10", "1.11", "1.12"]),
                                Lane("3.1.3", ["1.4", "1.8", "1.12"]), Lane("3.1.4", ["1.4", "1.8", "1.12"]), Lane("3.2.3", ["1.3", "1.7", "1.11"]),
                                Lane("3.2.4", ["1.3", "1.7", "1.11"]),
                                Lane("3.3.3", ["1.2", "1.5", "1.10"]), Lane("3.3.4", ["1.2", "1.5", "1.10"]), Lane("3.4.3", ["1.1", "1.5", "1.9"]),
                                Lane("3.4.4", ["1.1", "1.5", "1.9"])]


    def ManageTraffic(self, c):
        if (time.time() - self.timer) > 2 and self.state == "orange":
            self.setcurrentlanestrafficlights(c,"red")
            self.timer = time.time()
            self.state = "red"
        elif (time.time() - self.timer) > 5 and self.state == "green":
        	self.state = "orange"
        	self.timer = time.time()
        	self.setcurrentlanestrafficlights(c,"orange")
        elif (time.time() - self.timer > 4 and self.state == "red"):
            path = self.BestPath(self.alltriggeredlanes)
            if len(path) > 0:
	            self.currentlanes = path
	            self.setcurrentlanestrafficlights(c,"green")
	            self.state = "green"
	            self.timer = time.time()
	            self.debuglanes()
        return self.currentlanes

    def BestPath(self, a):
    	remaininglanes = list(a)
    	path = []
    	for remaininglane in remaininglanes:
    		goodlane = True
    		for dependedlane in remaininglane.dependedlanes:
    			for chosenlane in path:
    				if  dependedlane == chosenlane.id:
    					goodlane = False
    					break
    			if not goodlane:
    				break
    		if goodlane:
    			path.append(remaininglane)
    	return path

    def setcurrentlanestrafficlights(self, c, color):
    	for lane in self.currentlanes:
    		lane.trafficlightstatus = color
    	c.send(TrafficlightToJSON(self.currentlanes))

    def debuglanes(self):
        print "-----TRIGGERED-----"
        for lane in self.alltriggeredlanes:
            print lane.id
        print "=====CHOSEN====="
        for lane in self.currentlanes:
            print lane.id

def jdefault(o):
    if isinstance(o, set):
        return list(o)
    return o.__dict__


def TrafficlightToJSON(trafficinput):
    output = TrafficSendData()
    for x in trafficinput:
        newtrafficlightstatus = TrafficLight(x.id, x.trafficlightstatus)
        output.trafficLights.append(newtrafficlightstatus)
    return json.dumps(output, default=jdefault) + '\n'
