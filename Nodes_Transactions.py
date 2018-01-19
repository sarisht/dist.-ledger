# coding=UTF-8

import sys
from dht import *
import os
class Node:
	def __init__(self,address,total_nodes = 75,):
		"""   Reads address.txt and creates a dictionary with key as node number and stores the hostname(ip address) and port   """
		a = open("address.txt", "r").read().split()
		d = {}
		i = 0
		while i < len(a):
			d[int(a[i])] = {"ip": a[i+1], "port" : int(a[i+2])}
			i+=3
		self.address_stored = d
		self.address = address # Node address
		self.online = True # Whether the node is online/offline
		self.transaction_history = {'0_0' : Transaction('0_0',0,1,0,1000)}# Transaction history initiated as all money in node 1
		self.message_log = [] # stores all incoming messages
		self.dht = DHT(total_nodes)
		self.dht.insert(self.address)
		self.l_clock = 0
		self.ip_address= self.address_stored[self.address]["ip"]# IP address of the current node
		self.port = self.address_stored[self.address]["port"]# port of the current node
	def Offline(self):
		self.online = False # toggles online to offline for a node to go offline
	def create_trans_id(self,money_unspent):
		""" creates transaction id required for the transacttion, creates additional id if there is a secondary ttransaction e.g. if i refer 1000 but use only 10"""
		trans_id = ''
		trans_id = trans_id+ str(self.address)
		trans_id = trans_id + '_'
		trans_id1 = trans_id + str(self.l_clock)
		trans_id2 = ''
		if money_unspent == 0:
			self.l_clock+=1
		else:
			trans_id2 = trans_id + str(self.l_clock + 1)
			self.l_clock+=2
		return((trans_id1, trans_id2))
	def lamport_clock(self,t):
		if t > self.l_clock:
			self.l_clock = t
	def check_balance(self):
		""" Checks the balance stored in the node by iterating over unspent transactions with receiver as the current node.  """
		balance = 0
		for trans in self.transaction_history:
			if self.transaction_history[trans].receiver == self.address:
				if not self.transaction_history[trans].spent:
					balance += self.transaction_history[trans].amount
		return balance
	def verify(self,id1,sender,receiver,amount,trans_ids,id2='',store = True,witness= None):
		"""Verifies an incoming transaction with the references and stores it in the history if store is set as true"""
		amount = int(amount)
		money_in = 0
		for trans in trans_ids:
			try:
				x = self.transaction_history[trans]
				if x.receiver == sender:
					if x.spent:
						return(False)
					else:
						money_in += x.amount
				else: return False
			except:
				return(False)
		if money_in < amount:
			return(False)
		if store:
			for trans in trans_ids:
				x = self.transaction_history[trans]
				x.spent = True
			money_unspent = money_in - amount
			t_main = Transaction(id1,sender,receiver,witness,amount)
			self.transaction_history[(t_main).ID] = t_main
			if money_unspent != 0:
				if id2 == '': return(False)
				t_sub  = Transaction(id2,sender,sender,witness,money_unspent)
				self.transaction_history[(t_sub).ID] = t_sub
		return(True)
	def send_history(self):
		"""Sends the history stored to a new incoming node"""
		sends = []
		for trans in self.transaction_history:
			sends.append(self.transaction_history[trans].sendable())
		return(sends)
	def convert(self, history_list):
		# Converts message to transaction history a list of Transactions
		self.transaction_history = {}
		for history in history_list:
			t = Transaction((history["ID"]),(history["initiator"]),history["receiver"],history["witness"],history["amount"],spent = history["spent"])
			self.transaction_history[history["ID"]] = t
		return True

class Transaction:
	local_trans_num = 1
	def __init__(self,id1,sender,receiver,witness,amount, spent=False):
		self.ID = id1
		self.initiator = sender
		self.receiver = receiver
		self.witness = witness
		self.amount = amount
		self.spent = spent
	def Spend(self):
		self.spent = True
	def sendable(self):
		data = { 
			"ID": self.ID,
			"initiator": self.initiator,
			"receiver" : self.receiver,
			"witness" : self.witness,
			"amount" : self.amount,
			"spent" : self.spent
			}
		return(data)
