import socket
import json   
from classes.TrafficLight import TrafficLightData, TrafficLight
from classes.Bridge import Bridge
from classes.Intersection import Intersection
from classes.UI import UI
from classes.ClientListenThread import ClientListenThread
import threading
from time import sleep   
import time 
from collections import namedtuple

class Main():
	def __init__(self):
		self.bridgestatus = Bridge()
		self.intersectionstatus = Intersection()
		self.UI = UI("Controller", self.intersectionstatus.carlanes, self.intersectionstatus.bicyclelanes,
		 self.intersectionstatus.pedestrianlanes, self.bridgestatus.carlanes + self.bridgestatus.boatlanes)
		self.port = 12478
		self.socket = self.socketSetup()
		self.timescale = 0

    #Main loop
	def run(self):
		self.UI.start()
		self.socket = self.waitForClient()
		ListenThread = ClientListenThread(self.socket,True, self.bridgestatus, self.intersectionstatus, self.UI)
		ListenThread.start()
		self.resetTrafficLights()
		sleep(4)
   		while True:
	   		self.UI.update(self.intersectionstatus.manageTraffic(self.socket))
	   		bridegeopen, brideopened, bridgelanes = self.bridgestatus.manageBridge(self.socket)
	   		self.UI.update(bridgelanes)
			self.UI.updateBridgeStatus(bridegeopen, brideopened)

	#Sends request to reset all trafficlights
	def resetTrafficLights(self):
		self.socket.send(TrafficLightData(self.intersectionstatus.carlanes+self.intersectionstatus.bicyclelanes+self.bridgestatus.carlanes+self.bridgestatus.boatlanes).classToJSON())
		sleep(0.1)
		self.socket.send(TrafficLightData(self.intersectionstatus.pedestrianlanes).classToJSON())

	#Setup for the socket to listen on a port
	def socketSetup(self):
		newsocket = socket.socket()         
		newsocket.bind(('', self.port))
		newsocket.listen(5)     
		print "socket is listening on port: %s" %(self.port) 
		return newsocket

	#Waits for client to connect to socket
	def waitForClient(self):
	   	newsocket, address = self.socket.accept()
	   	print 'Got connection from', address
	   	return newsocket

main = Main()
main.run()