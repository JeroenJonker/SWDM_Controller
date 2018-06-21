import socket
import json   
from classes.TrafficLight import TrafficLightData, TrafficLight
from classes.Bridge import Bridge
from classes.Intersection import Intersection
from classes.UI import UIhread
from classes.ClientListenThread import ClientListenThread
import threading
from time import sleep   
import time 
from collections import namedtuple

class Main():
	def __init__(self):
		self.bridgestatus = Bridge()
		self.intersectionstatus = Intersection()
		self.UI = UIhread("Controller", self.intersectionstatus.carlanes, self.intersectionstatus.bicyclelanes,
		 self.intersectionstatus.pedestrianlanes, self.bridgestatus.carlanes + self.bridgestatus.boatlanes)
		self.port = 12478
		self.socket = self.SocketSetup()
		self.timescale = 0

	def run(self):
		self.UI.start()
		self.socket = self.WaitForClient()
		ListenThread = ClientListenThread("ClientListenThread",self.socket,True, self.bridgestatus, self.intersectionstatus, self.UI)
		ListenThread.start()
		self.initialetrafficlights()
		sleep(4)
   		while True:
	   		self.UI.update(self.intersectionstatus.ManageTraffic(self.socket))
	   		bridegeopen, brideopened, bridgelanes = self.bridgestatus.ManageBridge(self.socket)
	   		self.UI.update(bridgelanes)
			self.UI.updateBridgeStatus(bridegeopen, brideopened)

	def initialetrafficlights(self):
		self.socket.send(TrafficLightData(self.intersectionstatus.carlanes+self.intersectionstatus.bicyclelanes+self.bridgestatus.carlanes+self.bridgestatus.boatlanes).ClassToJSON())
		sleep(0.1)
		self.socket.send(TrafficLightData(self.intersectionstatus.pedestrianlanes).ClassToJSON())

	def SocketSetup(self):
		newsocket = socket.socket()         
		newsocket.bind(('', self.port))
		newsocket.listen(5)     
		print "socket is listening on port: %s" %(self.port) 
		return newsocket

	def WaitForClient(self):
	   	newsocket, address = self.socket.accept()
	   	print 'Got connection from', address
	   	return newsocket

main = Main()
main.run()