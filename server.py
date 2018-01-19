import socket
import json
import keyboard

class Server(object):
	"""docstring for Server"""
	def __init__(self, max_requests = 5, hostname = socket.gethostname()):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind((hostname, 8000))
		self.s.listen(max_requests)
		self.start()

	def start(self):
		while True:
			soc,addr = self.s.accept()
			data = soc.recv(1024)
			self.updates(data)
			print data
			soc.sendall("sent successfully") # add the correct mssg
			if keyboard.is_pressed("q"):
				soc.close()
				break
	def updates(self, data):
		pass
Server()