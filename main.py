import socket
import json   
from classes.TrafficLight import TrafficSendData, TrafficLight
from classes.Bridge import Bridge
from classes.Intersection import Intersection
from classes.UI import UIhread
import threading
from time import sleep   
import time 
from collections import namedtuple
# from classes.Lane import Lane

class ClientListenhread(threading.Thread):
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
		received = self.c.recv(2048)
		if (len(received) > 0):
			received = (received).strip().lower()
			print received
			#In python3 .decode('utf-8') / .encode('utf-8') nodig bij received
			splittedmessage = received.split('\n')
			for message in splittedmessage:
				# print "this is message: " + str(message)
				newinfo = json.loads(message, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
				self.UpdateTriggers(newinfo)

	def UpdateTriggers(self,updatedtriggers):
	 	# updatedtriggers.type == "secondarytrigger, nothing is done with this"
		if (updatedtriggers.type == "primarytrigger"):
			self.UpdateTriggerLanes(updatedtriggers)
		elif (updatedtriggers.type == "bridgestatusdata"):
			bridgestatus.bridgeopened = updatedtriggers.opened
			UI.updateBridgeStatus(bridgestatus.bridgeopen, bridgestatus.bridgeopened)
		elif (updatedtriggers.type == "timescaledata"):
			self.ConfirmTimescale(self.c, updatedtriggers)

	def UpdateTriggerLanes(self,updatedtrigger):
		if self.UpdateSpecificLanesIntersection(updatedtrigger, intersectionstatus.carlanes): return
		if self.UpdateSpecificLanesIntersection(updatedtrigger, intersectionstatus.bicyclelanes): return
		if self.UpdateSpecificLanes(updatedtrigger, bridgestatus.carlanes): return
		if self.UpdateSpecificLanes(updatedtrigger, bridgestatus.boatlanes): return
		if self.UpdateSpecificLanesIntersection(updatedtrigger, intersectionstatus.pedestrianlanes): return

	def UpdateSpecificLanes(self,updatedtrigger,specificlanes):
		for lane in specificlanes:
			if updatedtrigger.id == lane.id:
				if (updatedtrigger.triggered):
					lane.triggered = 1
				else:
					lane.triggered = 0
				return True
		return False

	def UpdateSpecificLanesIntersection(self,updatedtrigger,specificlanes):
		for lane in specificlanes:
			if updatedtrigger.id == lane.id:
				if (updatedtrigger.triggered) and not lane in intersectionstatus.alltriggeredlanes:
					intersectionstatus.alltriggeredlanes.append(lane)
					lane.triggered += 1
				elif lane in intersectionstatus.alltriggeredlanes and lane in intersectionstatus.alltriggeredlanes:
					intersectionstatus.alltriggeredlanes.remove(lane)
					lane.triggered -= 1
				return True
		return False

	def ConfirmTimescale(self, c, updatedtriggers):
		global timescale 
		timescale = updatedtriggers.scale
		c.send(json.dumps({'type':'TimeScaleVerifyData', 'status':False}) +'\n')

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

def WaitForClient(socket):
   	c, addr = socket.accept()
   	print 'Got connection from', addr
   	return c

def TrafficlightToJSON(trafficinput):
	output = TrafficSendData()
	for x in trafficinput:
		newtrafficlightstatus = TrafficLight(x.id, x.trafficlightstatus)
		output.trafficLights.append(newtrafficlightstatus)
	return json.dumps(output, default=jdefault) + '\n'

def initialetrafficlights(c):
	c.send(TrafficlightToJSON(intersectionstatus.carlanes+intersectionstatus.bicyclelanes+bridgestatus.carlanes+bridgestatus.boatlanes))
	sleep(0.1)
	c.send(TrafficlightToJSON(intersectionstatus.pedestrianlanes))

def main(port):
	socket = SocketSetup(port)
	c = WaitForClient(socket)
	ListenThread = ClientListenhread("ClientListenThread",c,True)
   	ListenThread.start()
   	initialetrafficlights(c)
   	sleep(4)
   	while True:
   		UI.update(intersectionstatus.ManageTraffic(c))
   		bridegeopen, brideopened, bridgelanes = bridgestatus.ManageBridge(c)
   		UI.update(bridgelanes)
		UI.updateBridgeStatus(bridegeopen, brideopened)

port = 12478
bridgestatus = Bridge()
intersectionstatus = Intersection()
timescale = 0
UI = UIhread("Controller", intersectionstatus.carlanes, intersectionstatus.bicyclelanes, intersectionstatus.pedestrianlanes, bridgestatus.carlanes + bridgestatus.boatlanes)
UI.start()
main(port)