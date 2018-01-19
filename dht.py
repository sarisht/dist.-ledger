# coding=UTF-8
import os
class DHT():
	"""This class implements the distributed hash table
	   It is assumed that each node stores its own public key for the hash table.
	"""
	def __init__(self, nodes = 75):
		self.nodes = nodes

	def initialize(self, path = ""):
		"""
		This function generates the public key for all the nodes that could exist and stores them in a file
		with the follow name format:
			path<node_no>_public_key.txt
		Do not call this fn while making the transactions, as this is not required
		"""
		if not os.path.exists(path):
			os.makedirs(path)
		for i in range(self.nodes):
			open(path+str(i+1)+"_public_key.txt", "w").write(str(i+1)+"abcxvz")

	def get_value(self, key):
		if str(key) == self.public_key[:-6]:
			return self.public_key

	def delete(self):
		pass
		
	def insert(self, node_id):
		"""
		This function reads the public key of the current node.
		"""
		self.public_key = open("keys/"+str(node_id)+"_public_key.txt", "r").readlines()[0].strip()
DHT().initialize("./keys/")
