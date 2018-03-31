import socket
import json   
from classes.TrafficLight import TrafficStuff
# from classes.MThread import MThread
import threading
from time import sleep    
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
		# print received
		if (len(received) > 0):
			#In python3 .decode('utf-8') / .encode('utf-8') nodig bij received
			newinfo = json.loads(received, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
			# print newinfo
			UpdateTriggers(newinfo)

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

def JSONOutput():
	traffic = TrafficStuff()
	traffic.trafficLights[1].lightStatus = "green"
	return json.dumps(traffic, default=jdefault) + '\n'

def WaitForClient(socket):
   	c, addr = socket.accept()
   	print 'Got connection from', addr
   	return c

def UpdateTriggers(updatedtriggers):
	if (updatedtriggers.type == "PrimaryTrigger"):
		UpdateTriggerLanes(updatedtriggers)
	elif (updatedtriggers.type == "SecondaryTrigger"):
		UpdateTriggerLanes(updatedtriggers)
		# oplossen bridgeopened en timescale niet de globale variabelen veranderen ]:)
	elif (updatedtriggers.type == "BridgeStatusData"):
		bridgeopened = updatedtriggers.opened
	elif (updatedtriggers.type == "TimeScaleData"):
		timescale = updatedtriggers.scale


def UpdateTriggerLanes(updatedtrigger):
	for lane in lanes:
		if (updatedtrigger.id == lane.id):
			if (updatedtrigger.triggered):
				lane.triggered += 1
			else:
				lane.triggered -= 1
			break

def ManageTraffic(c):
	sleep(5)
	alltriggeredlanes = gettriggeredlanes()
	resettrafficlights()
	if not (alltriggeredlanes == []):
		mostlanespath, mostlanespathprioritylanes = RecursionSearch(alltriggeredlanes, lanes, [], [])
		setlanetrafficlights(mostlanespath, "green")

def setlanetrafficlights(setlanes, color):
	for setlane in setlanes:
		sleep(0.3)
		#print "optimallane: " + str(optimallane.id)
		for lane in lanes:
			if setlane.id == lane.id:
				lane.trafficlightstatus = color
	# for lane in lanes:
	# 	sleep(0.3)
	# 	print str(lane.id) + ":" + str(lane.trafficlightstatus)

def resettrafficlights():
	for lane in lanes:
		lane.trafficlightstatus = "red"

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
			copyofremaininglanes = CopyOfListWithoutObject(remaininglanes,remaininglane)
			copyofcurrentlanes = CopyOfListWithObject(currentlanes,remaininglane)
			copyofnotusablelanes = AddLanesFromListOfIDs(notusablelanes,remaininglane.dependedlanes)
			mostlanespath1, mostlanespathprioritylanes1 = RecursionSearch(remainingprioritylanes, copyofremaininglanes, copyofcurrentlanes, copyofnotusablelanes)
			if (len(mostlanespathprioritylanes1) < len(leastremainingprioritylanes) or
				(len(mostlanespathprioritylanes1) == len(leastremainingprioritylanes) and len(mostlanespath1) > len(mostlanespath))):
				mostlanespath = mostlanespath1
				leastremainingprioritylanes = mostlanespathprioritylanes1
	return mostlanespath, leastremainingprioritylanes


def main(port):
	socket = SocketSetup(port)
	message = JSONOutput()
	c = WaitForClient(socket)
	ListenThread = MThread("ClientListenThread",c,True)
   	ListenThread.start()
   	while True:
   		ManageTraffic(c)
	   	# c.send(message)

def InitLanes(lanedependencies):
	lanes = []
	for x in range(0,len(lanedependencies)):
		lanes.append(Lane(str(x+1),lanedependencies[x]))
	return lanes

port = 12475
lanedependencies = [[5,9],[5,9,10,11,12],[5,7,8,9,11,12],[8,12,6],[1,2,3,8,9,11,12],[4,5],
					[3,11],[3,4,5,11,12],[1,2,3,5,11,12],[2,5],[2,3,5,8,7,9],[2,3,4,5,8,9]]
lanes = InitLanes(lanedependencies)
bridgeopened = False
timescale = 0
main(port)
