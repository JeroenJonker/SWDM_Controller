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
        # self.primarytriggeredlanes = []
        # self.secondarytriggeredlanes = []
        self.state = "red"
        self.carlanes = [Lane("1.1", [5, 9]), Lane("1.2", [5, 9, 10, 11, 12]), Lane("1.3", [5, 6, 7, 8, 9, 11, 12]),
                         Lane("1.4", [6, 8, 12]),
                         Lane("1.5", [1, 2, 3, 6, 8, 9, 10, 11, 12]), Lane("1.6", [3, 4, 5, 7, 11]), Lane("1.7", [3, 6, 11]),
                         Lane("1.8", [3, 4, 5, 11, 12]),
                         Lane("1.9", [1, 2, 3, 5, 11, 12]), Lane("1.10", [2, 5]), Lane("1.11", [2, 3, 5, 6, 7, 8, 9]),
                         Lane("1.12", [2, 3, 4, 5, 8, 9])]
        self.bicyclelanes = [Lane("2.1", [1, 2, 3, 4, 8, 12]), Lane("2.2", [3, 4, 5, 7, 11]),
                             Lane("2.3", [2, 5, 7, 8, 9, 10]), Lane("2.4", [1, 5, 9, 10, 11, 12])]
        self.pedestrianlanes = [Lane("3.1.1", [1, 2, 3]), Lane("3.1.3", [1, 2, 3]), Lane("3.2.1", [5, 4]),
                                Lane("3.2.3", [5, 4]),
                                Lane("3.3.1", [7, 8, 9]), Lane("3.3.3", [7, 8, 9]), Lane("3.4.1", [10, 11, 12]),
                                Lane("3.4.3", [10, 11, 12]),
                                Lane("3.1.2", [4, 8, 12]), Lane("3.1.4", [4, 8, 12]), Lane("3.2.2", [3, 7, 11]),
                                Lane("3.2.4", [3, 7, 11]),
                                Lane("3.3.2", [2, 5, 10]), Lane("3.3.4", [2, 5, 10]), Lane("3.4.2", [1, 5, 9]),
                                Lane("3.4.4", [1, 5, 9])]


    def ManageTraffic(self, c):
        if (time.time() - self.timer) > 11 and self.state == "orange":
            self.setcurrentlanestrafficlights(c,"red")
            self.timer = time.time()
            self.state = "red"
            print self.state
        elif (time.time() - self.timer) > 9 and self.state == "green":
        	self.state = "orange"
        	self.setcurrentlanestrafficlights(c,"orange")
        elif (time.time() - self.timer > 4 and self.state == "red"):
            self.currentlanes = self.BestPath(self.alltriggeredlanes, [])
            self.setcurrentlanestrafficlights(c,"green")
            self.state = "green"
            self.debuglanes()
        return self.currentlanes

    def BestPath(self, remaininglanes, chosenlanes):
    	for remaininglane in remaininglanes:
    		goodlane = True
    		for dependedlane in remaininglane.dependedlanes:
    			for chosenlane in chosenlanes:
    				if "1." + str(dependedlane) == chosenlane.id:
    					goodlane = False
    					break
    			if not goodlane:
    				break
    		if goodlane:
    			chosenlanes.append(remaininglane)
    			copyremaininglanes = list(remaininglanes)
    			copyremaininglanes.remove(remaininglane)
    			for dependedlane in remaininglane.dependedlanes:
    				for copyremaininglane in copyremaininglanes:
    					if "1." + str(dependedlane) == copyremaininglane.id:
    						copyremaininglanes.remove(copyremaininglane)
    						break
    			return self.BestPath(copyremaininglanes, chosenlanes)
    	return chosenlanes

    def setcurrentlanestrafficlights(self, c, color):
    	for lane in self.currentlanes:
    		lane.trafficlightstatus = color
    	c.send(TrafficlightToJSON(self.currentlanes))

    def debuglanes(self):
        for lane in self.alltriggeredlanes:
            print lane.id
        print "=========="
        for lane in self.currentlanes:
            print lane.id
        print "---------------"

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
