import socket
import json   
from classes.TrafficLight import TrafficStuff
from classes.TrafficLight import trafficLight
from classes.Bridge import Bridge
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
	print updatedtriggers
	if (updatedtriggers.type == "PrimaryTrigger"):
		UpdateTriggerLanes(updatedtriggers)
	elif (updatedtriggers.type == "SecondaryTrigger"):
		UpdateTriggerLanes(updatedtriggers)
	elif (updatedtriggers.type == "BridgeStatusData"):
		bridgestatus.bridgeopened = updatedtriggers.opened
		# print bridgestatus.bridgeopened
		# print bridgestatus.bridgeopen
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
	for lane in lanes:
		if (updatedtrigger.id == lane.id):
			if (updatedtrigger.triggered):
				lane.triggered += 1
			else:
				lane.triggered -= 1
			return
	for lane in bridgelanes:
		if updatedtrigger.id == lane.id:
			if (updatedtrigger.triggered):
				lane.triggered += 1
			else:
				lane.triggered -= 1
			return

def ManageTraffic(c, timer):
	# sleep(5)
	# alltriggeredlanes = gettriggeredlanes()
	# if not (alltriggeredlanes == []):
	# 	resettrafficlights(c)
	# 	mostlanespath, mostlanespathprioritylanes = RecursionSearch(alltriggeredlanes, lanes, [], [])
	# 	setlanetrafficlights(mostlanespath, "green")
	# 	c.send(TrafficlightToJSON(mostlanespath))
	ManageBridge(c)

def setlanetrafficlights(setlanes, color):
	for setlane in setlanes:
		sleep(0.3)
		#print "optimallane: " + str(optimallane.id)
		for lane in lanes:
			if setlane.id == lane.id:
				lane.trafficlightstatus = color
	for lane in lanes:
		sleep(0.3)
		print str(lane.id) + ":" + str(lane.trafficlightstatus)

def resettrafficlights(c):
	newsetlanes = []
	for lane in lanes:
		if lane.trafficlightstatus == "green":
			lane.trafficlightstatus = "red"
			newsetlanes.append(lane)
	c.send(TrafficlightToJSON(newsetlanes))

def gettriggeredlanes():
	alltriggeredlanes = []
	for lane in lanes:
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
		for lane in lanes:
			if lane.id == str(laneid):
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


def main(port):
	socket = SocketSetup(port)
	c = WaitForClient(socket)
	ListenThread = MThread("ClientListenThread",c,True)
   	ListenThread.start()
   	while True:
   		ManageTraffic(c,0)

def InitLanes(lanedependencies):
	lanes = []
	for x in range(0,len(lanedependencies)):
		lanes.append(Lane(str(x+1),lanedependencies[x]))
	return lanes


port = 12477
lanedependencies = [[5,9],[5,9,10,11,12],[5,7,8,9,11,12],[8,12,6],[1,2,3,8,9,11,12],[4,5],
					[3,11],[3,4,5,11,12],[1,2,3,5,11,12],[2,5],[2,3,5,8,7,9],[2,3,4,5,8,9]]
lanes = InitLanes(lanedependencies)
bridgelanes = [Lane("1.13"),Lane("4.1"),Lane("4.2"),Lane("3.1"),Lane("2.1")]
bridgestatus = Bridge()
timescale = 0
main(port)