from Tkinter import *
import threading
from Lane import Lane

#Userinterface to keep track of the status of the lanes and brige
class UI(threading.Thread):
	def __init__(self, titlename, carlanes, bicyclelanes, pedestrianlanes, bridgelanes):
		threading.Thread.__init__(self)
		self.root = Tk()
		self.root.title(titlename)
		self.root.configure(background="#2C3E50")
		self.carframe = Frame(self.root, bg="#2C3E50")
		self.carframe.pack(side=LEFT)
		self.lanestates = self.lanesToLabels(carlanes, self.carframe)
		self.bicycleframe = Frame(self.root, bg="#2C3E50")
		self.bicycleframe.pack(side=LEFT)
		self.lanestates.update(self.lanesToLabels(bicyclelanes, self.bicycleframe))
		self.pedestrianframe = Frame(self.root, bg="#2C3E50")
		self.pedestrianframe.pack(side=LEFT)
		self.lanestates.update(self.lanesToLabels(pedestrianlanes, self.pedestrianframe))
		self.bridgeframe = Frame(self.root,bg="#2C3E50")
		self.bridgeframe.pack(side=LEFT)
		self.lanestates.update(self.lanesToLabels(bridgelanes, self.bridgeframe))
		self.bridgeopen = Label(self.bridgeframe, text="bridgerequeststatus", fg="#ECF0F1" ,bg="#2C3E50").grid(row=4, column=1)
		self.bridgeopenstatus = Label(self.bridgeframe, bg="red")
		self.bridgeopenstatus.grid(row=4, column=0)
		self.bridgeopened = Label(self.bridgeframe, text="bridgeopenstatus", fg="#ECF0F1" ,bg="#2C3E50").grid(row=5, column=1)
		self.bridgeopenedstatus = Label(self.bridgeframe, bg="red")
		self.bridgeopenedstatus.grid(row=5, column=0)

	#Creates a label for each lane in an array of lanes for the UI and puts it in a frame
	def lanesToLabels(self,lanes, frame):
		states = {}
		counter = 0
		for lane in lanes:
			label = Label(frame, text="Trafficlight: "+ lane.id, fg="#ECF0F1" ,bg="#2C3E50").grid(row=counter, column=1)
			status = Label(frame, bg=lane.trafficlightstatus)
			states.update({lane.id : status})
			status.grid(row=counter, column=0)
			counter += 1
		return states

	#main loop
	def run(self):
		print "Starting UI"
		self.root.mainloop()
		print "exiting UI"

	#Updates the newly set lanes for the UI
	def update(self, newsetlanes):
		for newsetlane in newsetlanes:
			if self.lanestates.get(newsetlane.id):
				self.lanestates[newsetlane.id].configure(bg=newsetlane.trafficlightstatus)

	#Updates the bridgestatus for the UI
	def updateBridgeStatus(self, bridgestatus, bridgestatusopened):
		if bridgestatus:
			self.bridgeopenstatus.configure(bg="green")
		else:
			self.bridgeopenstatus.configure(bg="red")
		if bridgestatusopened:
			self.bridgeopenedstatus.configure(bg="green")
		else:
			self.bridgeopenedstatus.configure(bg="red")