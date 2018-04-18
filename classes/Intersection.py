from Lane import Lane
import time
from time import sleep
from TrafficLight import TrafficSendData, TrafficLight
import json  

class Intersection(object):
	def __init__(self):
		self.currentlanes = []
		self.timer = 0
		self.primarytriggeredlanes = []
		self.secondarytriggeredlanes = []
		self.resseted = False
		self.carlanes = [Lane("1.1",[5,9]),Lane("1.2",[5,9,10,11,12]),Lane("1.3",[5,6,7,8,9,11,12]),Lane("1.4",[8,12,6]),
						Lane("1.5",[1,2,3,8,9,11,12]),Lane("1.6",[3,4,5,7,11]),Lane("1.7",[3,6,11]),Lane("1.8",[3,4,5,11,12]),
						Lane("1.9",[1,2,3,5,11,12]),Lane("1.10",[2,5]),Lane("1.11",[2,3,5,6,8,7,9]),Lane("1.12",[2,3,4,5,8,9])]
		self.bicyclelanes = [Lane("2.1",[1,2,3,4,8,12]),Lane("2.2",[3,4,5,7,11]),Lane("2.3",[2,5,7,8,9,10]),Lane("2.4",[1,5,9,10,11,12])]
		self.pedestrianlanes = [Lane("3.1.1",[1,2,3]),Lane("3.1.3",[1,2,3]),Lane("3.2.1",[5,4]),Lane("3.2.3",[5,4]),
				   Lane("3.3.1",[7,8,9]),Lane("3.3.3",[7,8,9]),Lane("3.4.1",[10,11,12]),Lane("3.4.3",[10,11,12]),
				   Lane("3.1.2",[4,8,12]),Lane("3.1.4",[4,8,12]),Lane("3.2.2",[3,7,11]),Lane("3.2.4",[3,7,11]),
				   Lane("3.3.2",[2,5,10]),Lane("3.3.4",[2,5,10]),Lane("3.4.2",[1,5,9]),Lane("3.4.4",[1,5,9])]

	def getTriggeredLanes(self):
		return (self.secondarytriggeredlanes + self.primarytriggeredlanes)

	def getNewLanes(self, alltriggeredlanes):
		triggeredlanes = list(alltriggeredlanes)
		for triggerlane in triggeredlanes:
			if triggerlane in self.currentlanes:
				triggeredlanes.remove(triggerlane)
		return triggeredlanes

	def ManageTraffic(self, c):
		if (time.time() - self.timer) > 11:
			self.resettrafficlights(c)
			self.timer = time.time()
			self.resseted = True
		elif (time.time() - self.timer > 4 and self.resseted):
			alltriggeredlanes = self.getNewLanes(self.getTriggeredLanes())
			mostlanespath, mostlanespathprioritylanes = self.RecursionSearch(alltriggeredlanes, self.getNewLanes(self.carlanes), [])
			mostlanespath =self.searchbyciclelanes(mostlanespath,alltriggeredlanes)
			self.currentlanes = mostlanespath
			self.setlanetrafficlights(self.currentlanes, "green")
			c.send(TrafficlightToJSON(self.currentlanes))
			self.resseted = False
		return self.currentlanes

	def searchbyciclelanes(self,mostlanespath,triggeredlanes):
		allprioritylanes, allremaininglanes = getseperatedpriorityremaininglanes(mostlanespath, triggeredlanes)
		newlanes = []
		triggeredbicyclepedestrianlanes = gettriggeredlanes(self.bicyclelanes) + gettriggeredlanes(self.pedestrianlanes)
		for lane in triggeredbicyclepedestrianlanes:
			newlanes = newlanes + islaneinlanedependencies(lane, allprioritylanes)
		copynewlanes = list(newlanes)
		if len(newlanes) > 0:
			for lane in newlanes:
				lane.trafficlightstatus = "green"
			return newlanes + allprioritylanes + addremaininglanes(allremaininglanes, newlanes)
		else:
			return mostlanespath


	def setlanetrafficlights(self,setlanes, color):
		for setlane in setlanes:
			# sleep(0.3)
			#print "optimallane: " + str(optimallane.id)
			for lane in self.carlanes:
				if setlane.id == lane.id:
					lane.trafficlightstatus = color

	def resettrafficlights(self,c):
		newsetlanes = []
		for lane in self.currentlanes:
			if lane.trafficlightstatus == "green":
				lane.trafficlightstatus = "red"
				newsetlanes.append(lane)
		if newsetlanes != []:
			c.send(TrafficlightToJSON(newsetlanes))
		return newsetlanes

	def AddLanesFromListOfIDs(self, addlist, listids):
		newlist = list(addlist)
		for laneid in listids:
			carid = "1."+str(laneid)
			for lane in self.carlanes:
				if lane.id == str(carid):
					newlist.append(lane)
		return newlist

	def RecursionSearch(self,remainingprioritylanes, remaininglanes, currentlanes):
		bestpath = currentlanes
		leastprioritylanes = remainingprioritylanes
		for remainingprioritylane in remainingprioritylanes:
			if remainingprioritylane in remaininglanes:
				copyofremainingprioritylanes = self.GetRemainingLanes(remainingprioritylanes, remainingprioritylane)
				copyofremaininglanes = self.GetRemainingLanes(remaininglanes,remainingprioritylane)
				copyofcurrentlanes = CopyOfListWithObject(currentlanes,remainingprioritylane)
				mostlanespath, mostlanespathprioritylanes = self.RecursionSearch(copyofremainingprioritylanes, copyofremaininglanes, copyofcurrentlanes)
				if (len(mostlanespathprioritylanes) < len(leastprioritylanes) or
					(len(mostlanespathprioritylanes) == len(leastprioritylanes) and len(mostlanespath) > len(bestpath))):
					bestpath, leastprioritylanes = mostlanespath, mostlanespathprioritylanes
		for remaininglane in remaininglanes:
			copyofremaininglanes = self.GetRemainingLanes(remaininglanes,remaininglane)
			copyofcurrentlanes = CopyOfListWithObject(currentlanes,remaininglane)
			mostlanespath, mostlanespathprioritylanes = self.RecursionSearch(remainingprioritylanes, copyofremaininglanes, copyofcurrentlanes)
			if (len(mostlanespathprioritylanes) < len(leastprioritylanes) or
				(len(mostlanespathprioritylanes) == len(leastprioritylanes) and len(mostlanespath) > len(bestpath))):
				bestpath, leastprioritylanes = mostlanespath, mostlanespathprioritylanes
		return bestpath, leastprioritylanes

	def GetRemainingLanes(self, oldlist, newobject):
		newlist = list(oldlist)
		newlist.remove(newobject)
		for laneid in newobject.dependedlanes:
			carid = "1."+str(laneid)
			for lane in newlist:
				if lane.id == str(carid):
					newlist.remove(lane)
		return newlist

# def islaneinlanes(searchlane, lanes):
# 	for lane in lanes:
# 		if searchlane == lane:
# 			return True
# 	return False

# def CopyOfListWithoutObject(oldlist, removeobject):
# 	newlist = list(oldlist)
# 	newlist.remove(removeobject)
# 	return newlist

def CopyOfListWithObject(oldlist, addobject):
	newlist = list(oldlist)
	newlist.append(addobject)
	return newlist

def gettriggeredlanes(triggerlanes):
	alltriggeredlanes = []
	for lane in triggerlanes:
		if lane.triggered > 0:
			# (sleep(0.5))
			# print str(lane.id) + "is triggered: " + str(lane.triggered)
			alltriggeredlanes.append(lane)
	return alltriggeredlanes

def getseperatedpriorityremaininglanes(mostlanespath, triggeredlanes):
	allprioritylanes = []
	allremaininglanes = []
	for mostlane in mostlanespath:
		if mostlane in triggeredlanes:
			allprioritylanes.append(mostlane)
		else:
			allremaininglanes.append(mostlane)
	for lane in allprioritylanes:
		print "prio: " + lane.id
	for lane in allremaininglanes:
		print "rem: " + lane.id
	return allprioritylanes, allremaininglanes

def addremaininglanes(remaininglanes, newlanes):
	goodlanes = []
	for remaininglane in remaininglanes:
		goodlane = True
		for newlane in newlanes:
			for dependedlane in newlane.dependedlanes:
				if ("1."+str(dependedlane) == remaininglane.id):
					goodlane = False
		if goodlane:
			goodlanes.append(remaininglane)
	return goodlanes

def islaneinlanedependencies(inlane, priortylanes):
	for dependedlane in inlane.dependedlanes:
		for prioritylane in priortylanes:
			if ("1." + str(dependedlane)) == prioritylane.id:
				return []
	return [inlane]

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