import socket
import json   
from classes.TrafficLight import TrafficStuff
from classes.TrafficLight import trafficLight
from classes.Bridge import Bridge
from classes.Intersection import Intersection
from classes.UI import UIhread
import threading
from time import sleep   
import time 
from collections import namedtuple
from classes.Lane import Lane

class MThread(threading.Thread):
	def __init__(self, name, c, keep):
		threading.Thread.__init__(self)
		self.name = name
		self.c = c
		self.keep = keep

	def run(self):
		print "Starting " + self.name
		while self.keep: 
			self.listening()
		print "exiting" + self.name

	def listening(self):
		received = self.c.recv(1024)
		if (len(received) > 0):
			received = received[:-1]
			#In python3 .decode('utf-8') / .encode('utf-8') nodig bij received
			splittedmessage = received.split('\n')
			for message in splittedmessage:
				print "this is message: " + str(message)
				newinfo = json.loads(message, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
				UpdateTriggers(self.c,newinfo)

def ManageBridge(c):
	if (bridgestatus.bridgeopen == bridgestatus.bridgeopened):
		if bridgestatus.timer > 0 or bridgestatus.allboatspassed:
			if (time.time() - bridgestatus.timer) > 25 or bridgestatus.allboatspassed:
				bridgestatus.bridgeopen = not bridgestatus.bridgeopen
				SendBridgeData(c)
				bridgestatus.timer = 0
				bridgestatus.allboatspassed = False
		elif (not bridgestatus.bridgeopened):
			for lane in bridgelanes:
				if lane.id.find("4.") == 0 and lane.triggered:
					bridgestatus.timer = time.time()
		elif (bridgestatus.bridgeopened):
			bridgestatus.allboatspassed = True
			for lane in bridgelanes:
				if lane.id.find("4.") == 0 and lane.triggered:
					bridgestatus.allboatspassed = False
					break

def jdefault(o):
    if isinstance(o, set):
        return list(o)
    return o.__dict__

def SocketSetup(port):
	s = socket.socket()         
	s.bind(('', port))
	s.listen(5)     
	print "socket is listening on port: %s" %(port) 
	return s

def TrafficlightToJSON(trafficinput):
	output = TrafficStuff()
	for x in trafficinput:
		newtrafficlightstatus = trafficLight(x.id, x.trafficlightstatus)
		output.trafficLights.append(newtrafficlightstatus)
	return json.dumps(output, default=jdefault) + '\n'

def WaitForClient(socket):
   	c, addr = socket.accept()
   	print 'Got connection from', addr
   	return c

def UpdateTriggers(c,updatedtriggers):
	if (updatedtriggers.type == "PrimaryTrigger"):
		UpdateTriggerLanes(updatedtriggers)
	elif (updatedtriggers.type == "SecondaryTrigger"):
		UpdateTriggerLanes(updatedtriggers)
	elif (updatedtriggers.type == "BridgeStatusData"):
		bridgestatus.bridgeopened = updatedtriggers.opened
	elif (updatedtriggers.type == "TimeScaleData"):
		print "ok"
		# ConfirmTimescale(c, updatedtriggers)

def SendBridgeData(c):
	c.send(json.dumps({'type':'BridgeData','bridgeOpen':bridgestatus.bridgeopen})+'\n')

def ConfirmTimescale(c, updatedtriggers):
	global timescale 
	timescale = updatedtriggers.scale
	c.send(json.dumps({'type':'TimeScaleVerifyData', 'status':True}) +'\n')

def UpdateTriggerLanes(updatedtrigger):
	if UpdateIntersectionTriggerLanes(updatedtrigger, lanes): return
	if UpdateSpecificLanes(updatedtrigger, bicyclelanes): return
	if UpdateSpecificLanes(updatedtrigger, bridgelanes): return
	if UpdateSpecificLanes(updatedtrigger, pedestrianlanes): return

def UpdateSpecificLanes(updatedtrigger,specificlanes):
	for lane in specificlanes:
		if updatedtrigger.id == lane.id:
			if (updatedtrigger.triggered):
				lane.triggered += 1
			else:
				lane.triggered -= 1
			return True
	return False

def UpdateIntersectionTriggerLanes(updatedtrigger, specificlanes):
	for lane in specificlanes:
		if updatedtrigger.id == lane.id:
			if (updatedtrigger.triggered):
				lane.triggered += 1
				if lane.triggered == 2:
					intersectionstatus.secondarytriggeredlanes.append(lane)
					intersectionstatus.primarytriggeredlanes.remove(lane)
				elif lane.triggered == 1:
					intersectionstatus.primarytriggeredlanes.append(lane)
			else:
				lane.triggered -= 1
				if lane.triggered == 1:
					intersectionstatus.secondarytriggeredlanes.remove(lane)
					intersectionstatus.primarytriggeredlanes.append(lane)
				elif lane.triggered == 0:
					intersectionstatus.primarytriggeredlanes.remove(lane)
			return True
	return False

def ManageTraffic(c, timer):
	alltriggeredlanes = intersectionstatus.getNewTriggeredLanes()
	if not (alltriggeredlanes == []) and (time.time() - intersectionstatus.timer) > 11:
		resettrafficlights(c)
		intersectionstatus.timer = time.time()
		intersectionstatus.resseted = True
		mostlanespath, mostlanespathprioritylanes = RecursionSearch(alltriggeredlanes, lanes, [], [])
		mostlanespath = searchbyciclelanes(mostlanespath,alltriggeredlanes)
		intersectionstatus.currentlanes = mostlanespath
		setlanetrafficlights(intersectionstatus.currentlanes, "green")
	elif (time.time() - intersectionstatus.timer > 4 and intersectionstatus.resseted):
		UI.update(intersectionstatus.currentlanes)
		c.send(TrafficlightToJSON(intersectionstatus.currentlanes))
		intersectionstatus.resseted = False
	ManageBridge(c)

def searchbyciclelanes(mostlanespath,triggeredlanes):
	allprioritylanes, allremaininglanes = getseperatedpriorityremaininglanes(mostlanespath, triggeredlanes)
	newlanes = []
	triggeredbicyclepedestrianlanes = gettriggeredlanes(bicyclelanes) + gettriggeredlanes(pedestrianlanes)
	for lane in triggeredbicyclepedestrianlanes:
		newlanes = newlanes + islaneinlanedependencies(lane, allprioritylanes)
	copynewlanes = list(newlanes)
	if len(newlanes) > 0:
		return newlanes + allprioritylanes + addremaininglanes(allremaininglanes, newlanes)
	else:
		return mostlanespath

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

def setlanetrafficlights(setlanes, color):
	for setlane in setlanes:
		# sleep(0.3)
		#print "optimallane: " + str(optimallane.id)
		for lane in lanes:
			if setlane.id == lane.id:
				lane.trafficlightstatus = color
	for lane in lanes:
		sleep(0.01)
		print str(lane.id) + ":" + str(lane.trafficlightstatus)

def resettrafficlights(c):
	newsetlanes = []
	for lane in intersectionstatus.currentlanes:
		if lane.trafficlightstatus == "green":
			lane.trafficlightstatus = "red"
			newsetlanes.append(lane)
	if newsetlanes != []:
		UI.update(newsetlanes)
		c.send(TrafficlightToJSON(newsetlanes))

def gettriggeredlanes(triggerlanes):
	alltriggeredlanes = []
	for lane in triggerlanes:
		if lane.triggered > 0:
			# (sleep(0.5))
			# print str(lane.id) + "is triggered: " + str(lane.triggered)
			alltriggeredlanes.append(lane)
	return alltriggeredlanes

def islaneinlanes(searchlane, lanes):
	for lane in lanes:
		if searchlane == lane:
			return True
	return False

def CopyOfListWithoutObject(oldlist, removeobject):
	newlist = list(oldlist)
	newlist.remove(removeobject)
	return newlist

def CopyOfListWithObject(oldlist, addobject):
	newlist = list(oldlist)
	newlist.append(addobject)
	return newlist

def AddLanesFromListOfIDs(addlist, listids):
	newlist = list(addlist)
	for laneid in listids:
		carid = "1."+str(laneid)
		for lane in lanes:
			if lane.id == str(carid):
				newlist.append(lane)
	return newlist

def RecursionSearch(remainingprioritylanes, remaininglanes, currentlanes, notusablelanes):
	mostlanespath = currentlanes
	leastremainingprioritylanes = remainingprioritylanes
	for remainingprioritylane in remainingprioritylanes:
		if islaneinlanes(remainingprioritylane, remaininglanes) and not islaneinlanes(remainingprioritylane, notusablelanes):
			copyofremainingprioritylanes = CopyOfListWithoutObject(remainingprioritylanes, remainingprioritylane)
			# CheckBestPath(copyofremainingprioritylanes,currentlanes, remaininglanes, notusablelanes,remainingprioritylane, mostlanespath, leastremainingprioritylanes)
			copyofremaininglanes = CopyOfListWithoutObject(remaininglanes,remainingprioritylane)
			copyofcurrentlanes = CopyOfListWithObject(currentlanes,remainingprioritylane)
			copyofnotusablelanes = AddLanesFromListOfIDs(notusablelanes,remainingprioritylane.dependedlanes)
			mostlanespath1, mostlanespathprioritylanes1 = RecursionSearch(copyofremainingprioritylanes, copyofremaininglanes, copyofcurrentlanes, copyofnotusablelanes)
			if (len(mostlanespathprioritylanes1) < len(leastremainingprioritylanes) or
				(len(mostlanespathprioritylanes1) == len(leastremainingprioritylanes) and len(mostlanespath1) > len(mostlanespath))):
				mostlanespath = mostlanespath1
				leastremainingprioritylanes = mostlanespathprioritylanes1
	for remaininglane in remaininglanes:
		if not islaneinlanes(remaininglane,notusablelanes):
			# CheckBestPath(remainingprioritylanes,currentlanes, remaininglanes, remaininglane, notusablelanes, mostlanespath, leastremainingprioritylanes)
			copyofremaininglanes = CopyOfListWithoutObject(remaininglanes,remaininglane)
			copyofcurrentlanes = CopyOfListWithObject(currentlanes,remaininglane)
			copyofnotusablelanes = AddLanesFromListOfIDs(notusablelanes,remaininglane.dependedlanes)
			mostlanespath1, mostlanespathprioritylanes1 = RecursionSearch(remainingprioritylanes, copyofremaininglanes, copyofcurrentlanes, copyofnotusablelanes)
			if (len(mostlanespathprioritylanes1) < len(leastremainingprioritylanes) or
				(len(mostlanespathprioritylanes1) == len(leastremainingprioritylanes) and len(mostlanespath1) > len(mostlanespath))):
				mostlanespath = mostlanespath1
				leastremainingprioritylanes = mostlanespathprioritylanes1
	return mostlanespath, leastremainingprioritylanes

# def CheckBestPath(remainingprioritylanes,currentlanes, remaininglanes, currentlane, notusablelanes, mostlanespath, leastremainingprioritylanes):
# 	copyofremaininglanes = CopyOfListWithoutObject(remaininglanes,currentlane)
# 	copyofcurrentlanes = CopyOfListWithObject(currentlanes,currentlane)
# 	copyofnotusablelanes = AddLanesFromListOfIDs(notusablelanes,currentlane.dependedlanes)
# 	mostlanespath1, mostlanespathprioritylanes1 = RecursionSearch(remainingprioritylanes, copyofremaininglanes, copyofcurrentlanes, copyofnotusablelanes)
# 	if (len(mostlanespathprioritylanes1) < len(leastremainingprioritylanes) or
# 		(len(mostlanespathprioritylanes1) == len(leastremainingprioritylanes) and len(mostlanespath1) > len(mostlanespath))):
# 		mostlanespath = mostlanespath1
# 		leastremainingprioritylanes = mostlanespathprioritylanes1
# 	return mostlanespath, leastremainingprioritylanes

def initialetrafficlights(c):
	c.send(TrafficlightToJSON(lanes+bicyclelanes+bridgelanes))
	sleep(0.1)
	c.send(TrafficlightToJSON(pedestrianlanes))

def main(port):
	socket = SocketSetup(port)
	c = WaitForClient(socket)
	ListenThread = MThread("ClientListenThread",c,True)
   	ListenThread.start()
   	initialetrafficlights(c)
   	sleep(5)
   	while True:
   		ManageTraffic(c,0)

port = 12478
lanes = [Lane("1.1",[5,9]),Lane("1.2",[5,9,10,11,12]),Lane("1.3",[5,7,8,9,11,12]),Lane("1.4",[8,12,6]),
		Lane("1.5",[1,2,3,8,9,11,12]),Lane("1.6",[4,5]),Lane("1.7",[3,11]),Lane("1.8",[3,4,5,11,12]),
		Lane("1.9",[1,2,3,5,11,12]),Lane("1.10",[2,5]),Lane("1.11",[2,3,5,8,7,9]),Lane("1.12",[2,3,4,5,8,9])]
bicyclelanes = [Lane("2.1",[1,2,3,4,8,12]),Lane("2.2",[3,4,5,7,11]),Lane("2.3",[2,5,7,8,9,10]),Lane("2.4",[1,5,9,10,11,12])]
# pedestrianlanes = [Lane("3.1.1-3",[1,2,3]),Lane("3.2.1-3",[5,4]),Lane("3.3.1-3",[8,8,9]),Lane("3.4.1-3",[10,11,12]),
# 				  Lane("3.1.2-4",[4,8,12]),Lane("3.2.2-4",[3,7,11]),Lane("3.3.2-4",[2,5,10]),Lane("3.4.2-4",[1,5,9])]
pedestrianlanes = [Lane("3.1.1",[1,2,3]),Lane("3.1.3",[1,2,3]),Lane("3.2.1",[5,4]),Lane("3.2.3",[5,4]),
				   Lane("3.3.1",[8,8,9]),Lane("3.3.3",[8,8,9]),Lane("3.4.1",[10,11,12]),Lane("3.4.3",[10,11,12]),
				   Lane("3.1.2",[4,8,12]),Lane("3.1.4",[4,8,12]),Lane("3.2.2",[3,7,11]),Lane("3.2.4",[3,7,11]),
				   Lane("3.3.2",[2,5,10]),Lane("3.3.4",[2,5,10]),Lane("3.4.2",[1,5,9]),Lane("3.4.4",[1,5,9])]
bridgelanes = [Lane("1.13"),Lane("4.1"),Lane("4.2")]
bridgestatus = Bridge()
intersectionstatus = Intersection()
timescale = 0
bridgelanes[0].trafficlightstatus = "green"
UI = UIhread("TrafficUI", lanes, bicyclelanes, pedestrianlanes, False)
UI.start()
main(port)