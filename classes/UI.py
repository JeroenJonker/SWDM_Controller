from Tkinter import *
import threading
from Lane import Lane

#entry() voor tekstveld, en .get() om de uitkomst hiervan te pakken.
#.pack(fill=X) voor de gehele breedte
#(command=self.function) voor bijv buttons. command= lambda bestolor=color: self.printy(bestolor) voor for loop

class UIhread(threading.Thread):
	def __init__(self, titlename, carlanes, bicyclelanes, pedestrianlanes, bridgestatus):
		threading.Thread.__init__(self)
		self.root = Tk()
		self.root.title(titlename)
		self.root.configure(background="#2C3E50")
		self.carframe = Frame(self.root, bg="#2C3E50")
		self.carframe.pack(side=LEFT)
		self.lanestates = self.setstates(carlanes, self.carframe)
		self.bycicleframe = Frame(self.root, bg="#2C3E50")
		self.bycicleframe.pack(side=LEFT)
		self.lanestates.update(self.setstates(bicyclelanes, self.bycicleframe))
		self.pedestrianframe = Frame(self.root, bg="#2C3E50")
		self.pedestrianframe.pack(side=LEFT)
		self.lanestates.update(self.setstates(pedestrianlanes, self.pedestrianframe))
		self.bridgestatus = bridgestatus

	def setstates(self,lanes, frame):
		states = {}
		counter = 0
		for lane in lanes:
			label = Label(frame, text="Trafficlight: "+ lane.id, fg="#ECF0F1" ,bg="#2C3E50").grid(row=counter, column=1)
			status = Label(frame, bg=lane.trafficlightstatus)
			states.update({lane.id : status})
			status.grid(row=counter, column=0)
			counter += 1
		return states

	def run(self):
		print "Starting UI"
		self.root.mainloop()
		print "exiting UI"

	def update(self, newsetlanes):
		for newsetlane in newsetlanes:
			if self.lanestates.get(newsetlane.id):
				self.lanestates[newsetlane.id].configure(bg=newsetlane.trafficlightstatus)