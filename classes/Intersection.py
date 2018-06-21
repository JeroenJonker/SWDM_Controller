from Lane import Lane
import time
from time import sleep
from TrafficLight import TrafficLightData, TrafficLight
import json

#The intersection and other lanes that are influenced by the intersection. 
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

	#Main loop
    def manageTraffic(self, socket):
        if (time.time() - self.timer) > 2 and self.state == "orange":
            self.setCurrentlanesTrafficlights(socket,"red")
            self.timer = time.time()
            self.state = "red"
        elif (time.time() - self.timer) > 5 and self.state == "green":
        	self.state = "orange"
        	self.timer = time.time()
        	self.setCurrentlanesTrafficlights(socket,"orange")
        elif (time.time() - self.timer > 4 and self.state == "red"):
            path = self.chooseLanes(self.alltriggeredlanes)
            if len(path) > 0:
	            self.currentlanes = path
	            self.setCurrentlanesTrafficlights(socket,"green")
	            self.state = "green"
	            self.timer = time.time()
	            self.debugLanes()
        return self.currentlanes

    #Returns lanes that are triggered and do not collide with eachother
    def chooseLanes(self, triggeredlanes):
    	remaininglanes = list(triggeredlanes)
    	chosenlanes = []
    	for remaininglane in remaininglanes:
    		if not self.isDependedLaneInChosenlanes(remaininglane, chosenlanes):
    			chosenlanes.append(remaininglane)
    	return chosenlanes

    #Checks if the remaininglane dependedlanes are in conflict with the already chosenlanes
    def isDependedLaneInChosenlanes(self, remaininglane, chosenlanes):
    	for dependedlane in remaininglane.dependedlanes:
    		for chosenlane in chosenlanes:
    			if dependedlane == chosenlane.id:
    				return True
    	return False

    #Sets the currentlanes to a specific color and sends the data to the simulator
    def setCurrentlanesTrafficlights(self, socket, color):
    	for lane in self.currentlanes:
    		lane.trafficlightstatus = color
    	socket.send(TrafficLightData(self.currentlanes).classToJSON())

    #debug, to see which lanes are triggered and which lanes are chosen
    def debugLanes(self):
        print "-----TRIGGERED-----"
        for lane in self.alltriggeredlanes:
            print lane.id
        print "=====CHOSEN====="
        for lane in self.currentlanes:
            print lane.id