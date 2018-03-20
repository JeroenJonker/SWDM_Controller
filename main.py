import socket
import json   
from classes.TrafficLight import TrafficStuff
from time import sleep    
from collections import namedtuple

def listening(c):
	received = c.recv(1024)
	if (len(received) > 0):
		#In python3 .decode('utf-8') / .encode('utf-8') nodig bij received
		test = json.loads(received, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
		print test.triggered
		print test
		return True
	else:
		return False 

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

def JSONinput():
	traffic = TrafficStuff()
	traffic.trafficLights[1].lightStatus = "green"
	return json.dumps(traffic, default=jdefault) + '\n'

def WaitForClient(socket, message):
   	c, addr = socket.accept()     
   	print 'Got connection from', addr
   	c.send(message)
   	sleep(1)
   	while True:
   		if (listening(c)):
   			break
   	# c.send(message)
  	c.close()   

def main(port):
	socket = SocketSetup(port)
	message = JSONinput()
	while True:
		WaitForClient(socket, message)

port = 12403
main(port)