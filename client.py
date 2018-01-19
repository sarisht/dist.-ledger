import socket
import json
import keyboard
class Client(object):
	"""docstring for Client"""
	def __init__(self, hostname = socket.gethostname(), mssg = None):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((hostname, 8000))
		a = {
		"mssg_id" : 1,
		"mssg" : 
		}
		self.s.sendall(json.dumps(a))
		data = self.s.recv(1024)
		print data
		self.send()
		# self.s.close()
	def send(self):
		while 1:
			a = {
			"dds" : 1
			}
			self.s.sendall(json.dumps(a))

			print "fo"
			data = self.s.recv(1024)
			print data
			if keyboard.is_pressed("q"):
				break
Client()
		
