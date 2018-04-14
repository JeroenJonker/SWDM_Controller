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
	if UpdateIntersectionTriggerLanes(updatedtrigger, intersectionstatus.carlanes): return
	if UpdateSpecificLanes(updatedtrigger, intersectionstatus.bicyclelanes): return
	if UpdateSpecificLanes(updatedtrigger, bridgestatus.lanes): return
	if UpdateSpecificLanes(updatedtrigger, intersectionstatus.pedestrianlanes): return

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
	c.send(TrafficlightToJSON(intersectionstatus.carlanes+intersectionstatus.bicyclelanes+bridgestatus.lanes))
	sleep(0.1)
	c.send(TrafficlightToJSON(intersectionstatus.pedestrianlanes))

def main(port):
	socket = SocketSetup(port)
	c = WaitForClient(socket)
	ListenThread = MThread("ClientListenThread",c,True)
   	ListenThread.start()
   	initialetrafficlights(c)
   	sleep(5)
   	while True:
   		UI.update(intersectionstatus.ManageTraffic(c))
		bridgestatus.ManageBridge(c)

port = 12478
bridgestatus = Bridge()
intersectionstatus = Intersection()
timescale = 0
UI = UIhread("TrafficUI", intersectionstatus.carlanes, intersectionstatus.bicyclelanes, intersectionstatus.pedestrianlanes, False)
UI.start()
main(port)