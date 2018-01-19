# coding=UTF-8

import socket
import threading
import sys
import json
import Nodes_Transactions as nt
from dht import *
import time
"""Threaded implemention if server and client combined

Running this code: From terminal run:
	python threaded_server.py <node_no_1>
In a separate terminal window, run:
	python threaded_server.py <node_no_2>

To see if it works, try sending messages from 1st window to another
To send a message, first enter the node_no of the window to which the message is being sent
Eg: node_no_1
Then enter the message to be sent

This should be visible in the second window as well.
"""
class Data():
	"""This class handles the following
		 1. Prepare the data in form of dictionary for broadcasting over the network.
		 2. Manage, update the transactions received from the network.
	"""
	def __init__(self):
		pass


	def verify_trans(self,mssg):
		return True
	
	
	def verify(self, mssg, soc):
		"""
		This function verifies whether the trnsaction is actually sent is authentic by verifying the public key.
		
		Signature is constructed as following:
			<transaction_id>q<from>q<to>q<amt/bitcoing>w<public key>

		To check the validity we just compare the public keys obtained from active agent with the public key substring 
		of signature

		"""
		data = self.prepare_data(m_type = 13)
		soc.sendall(data)
		# data = soc.recv(1024)
		# print data
		public_key = json.loads(soc.recv(1024))
		if mssg["signature"].split("w")[1] == public_key["public_key"]:
			return True
		else:
			return False


	def manage_data(self, node_no, mssg, soc = None):
		"""
		This function handles the requests as appropriate that are received from other nodes in the network
		Args:
			 node_no : Number of the current node
			 mssg : message received from other node. Dictionary with structure as built in the prepare data.
		"""
		sent_time = mssg["time"]
		updated_time = max(n.l_clock, sent_time+1)
		n.l_clock = updated_time+1
		if mssg['message_id'] == 1:
			return self.prepare_data(m_type = 2)

		elif mssg["message_id"] == 3:
			if self.verify( mssg, soc):
				if n.verify(mssg["transaction_id1"], mssg["transfer_from"], n.address, mssg["transfer_amt"], mssg["reference"], store = False):
					print 'You have a commit request for the following: '
					print 'Sender:',
					print mssg["transfer_from"],
					print 'Amount:',
					print mssg["transfer_amt"]
					v = raw_input('Do you wish to commit as receiver for the reaction (Verified as valid automatically): (y/n)')
					if v == 'y': return self.prepare_data( m_type = 5)
					bool = True
			return self.prepare_data( m_type = 6)
		elif mssg["message_id"] == 4:
			if self.verify(mssg, soc):
				if n.verify(mssg["transaction_id1"], mssg["transfer_from"], mssg["transfer_to"], mssg["transfer_amt"], mssg["reference"], witness = n.address, store = False):
					print 'You have a commit request for the following: '
					print 'Sender:',
					print mssg["transfer_from"],
					print 'Receiver:',
					print mssg["transfer_to"],
					print 'Amount:',
					print mssg["transfer_amt"]
					v = raw_input('Do you wish to commit as a witness for the reaction (Verified as valid automatically): (y/n)')
					if v == 'y': return self.prepare_data( m_type = 5)
					bool = True
			return self.prepare_data( m_type = 6)
		elif mssg["message_id"] == 7:
			if self.verify(mssg, soc):
				if n.verify(mssg["transaction_id1"], mssg["transfer_from"], mssg["transfer_to"], mssg["transfer_amt"], trans_ids = mssg["reference"], witness = mssg["transfer_witness"], id2 = mssg["transaction_id2"]):
					return self.prepare_data(m_type = 11)
		elif mssg["message_id"] == 12:
			if self.verify( mssg, soc):
				return self.prepare_data( m_type = 11)
		elif mssg["message_id"] == 13:
			return self.prepare_data( m_type = 9)


	def prepare_data(self, transfer_from = None, transfer_to = None, transfer_witness = None, amt = None, 
					unsyn_nodes = None, m_type = None, transaction_id1 = None, transaction_id2 = None, public_key = None, reference = None):
		"""
		This function creates a json dicitionary object for broadcasting it over the network
		Args:
			 unsyn_nodes : array nodes that couldnt update the transaction with given t_id
			 m_type : type of message for sending over the network. The key is there in the design doc
			 		  e.g. m_type = 4 - message is meant for broadcasting and finding a witness
		"""
		data = None
			
		if m_type == 1:# update transaction history request 
			data = {
				"message_from" :n.address,
				"message_id" : 1,
				"time" : n.l_clock
			}
			
		elif m_type == 2:
			data = {
				"message_from" :n.address,
				"message_id" : 2,
				"transactions" : n.send_history(),
				"time" : n.l_clock
			}
			
		elif m_type == 3:
			data = {
				"message_from" :n.address,
				"transaction_id1" : transaction_id1,
				"message_id" : 3,
				"transfer_from" : transfer_from,
				"transfer_amt" : amt,
				"signature" : str(transaction_id1)+"q"+str(transfer_from)+"q"+amt+"w"+self.dht.get_value(self.node),
				"reference" : reference,
				"time" : n.l_clock
			}
			
		elif m_type == 4:
			data = {
				"message_from" :n.address,
				"transaction_id1" : transaction_id1,
				"message_id" : 4,
				"transfer_from" : transfer_from,
				"transfer_to" : transfer_to,
				"transfer_witness" : transfer_witness,
				"transfer_amt" : amt,
				"signature" : str(transaction_id1)+"q"+str(transfer_from)+"q"+str(transfer_to)+"q"+amt+"w"+self.dht.get_value(self.node),
				"reference" : reference,
				"time" : n.l_clock
			}
			
		elif m_type == 5:
			data = {
				"message_from" :n.address,
				"message_id" : 5,
				"time" : n.l_clock
			}
			
		elif m_type == 6:
			data = {
				"message_from" :n.address,
				"message_id" : 6,
				"time" : n.l_clock
			}
			
		elif m_type == 7:
			data = {
				"message_from" :n.address,
				"transaction_id1" : transaction_id1,
				"transaction_id2" : transaction_id2,
				"message_id" : 7,
				"transfer_from" : transfer_from,
				"transfer_to" : transfer_to,
				"transfer_witness" : transfer_witness,
				"transfer_amt" : amt,
				"signature" : str(transaction_id1)+"q"+str(transfer_from)+"q"+str(transfer_to)+"q"+amt+"w"+self.dht.get_value(self.node),
				"reference" : reference,
				"time" : n.l_clock

			}
			
		elif m_type == 9:
			data = {
				"message_from" :n.address,
				"message_id" : 9,
				"public_key" : self.dht.get_value(self.node),
				"time" : n.l_clock
			}
			
		elif m_type == 11:
			data = {
				"message_from" :n.address,
				"message_id" : 11,
				"time" : n.l_clock
			}
			
		elif m_type == 12:
			data = {
				"message_from" :n.address,
				"transaction_id1" : transaction_id1,
				"transaction_id2" : transaction_id2,
				"message_id" : 12,
				"transfer_from" : transfer_from,
				"transfer_to" : transfer_to,
				"transfer_witness" : transfer_witness,
				"transfer_amt" : amt,
				"unsynced_nodes" : unsyn_nodes,
				"signature" : str(transaction_id1)+"q"+str(transfer_from)+"q"+str(transfer_to)+"q"+amt+"w"+self.dht.get_value(self.node),
				"time" : n.l_clock
			}
		elif m_type == 13: # ask for the public key
			data = {
				"message_from" :n.address,
				"message_id" : 13,
				"time" : n.l_clock
			}
			
		if data == None:
			data = {}
		n.l_clock+=1
		return json.dumps(data)




class Active(threading.Thread, Data):
	"""Active corresponds to the client side of the code
	This actively sends messages rather than just apassively waiting for incoming connections
	"""
	def __init__(self, name, node_no, dht, total_nodes = 10):
		"""
		Args:
			name: Name for this thread. By convention, it should be of the form Node_<int>_Active, where <int> denotes the Node_No for this client
			node_no: Node_no for this node (Common for both active and passive threads)
			dht : It is the distributed hash table that returns the value corresponding to key given.

		"""
		threading.Thread.__init__(self)
		self.name = name
		self.node = node_no
		self.total_nodes = total_nodes
		self.dht = dht

	def run(self):
		print("Starting thread "+self.name)
		self.active_messaging( self.name, 100)
		print("Closing thread "+self.name)

	def get_seller_agreement(self, name, node, txt, ref):
		"""
		This function sends a request to the mssg receiver,
		if he wants to make the transaction or not.
		"""
		mssg = self.prepare_data(name, node, amt = txt, m_type = 3, reference = ref) 
		return self.send_message(name, node, mssg, True)

	def get_witness(self, name, node, txt, ref):
		"""
		This function returns the node that agrees to witness to transaction
		between name and node varable. It returns -1 if no consents to be the
		witness.
		"""
		mssg = self.prepare_data(name, node, amt = txt, m_type = 4, reference = ref)
		for nod in xrange(1, self.total_nodes + 1):
			try:
				status = self.send_message(name, nod, mssg, True)
				if status:
					return nod	
			except Exception as e:
				continue
			
		return -1
	def send_witness(self, name, node, witness, txt, ref):
		mssg = self.prepare_data(name, node, transfer_witness = witness, amt = txt, m_type = 4, reference = ref)
		return self.send_message(name, witness, mssg, True)

	def send_to_all(self, name, node, witness, txt,id1,id2, unsync = None, m_type = 7, reference = None):
		"""
		This function sends data from current node to all the nodes in the network
		
		m_type : 

		7 : Broadcast the transaction between "name" and "node" to all other nodes and
			return the nodes that didnt update the transaction in their ledger
		12 : Broadcasts the list of unsynced node of the the transaction between "name" and
			 "node" to all other nodes and returns the appropriate status
		"""
		if m_type == 7:
			trans_data = self.prepare_data(name, node, witness, txt,transaction_id1 = id1, transaction_id2 =id2, m_type = 7, reference = reference)	
			unsynced = []
			for nod in xrange(1, self.total_nodes + 1):
				try:
					status = self.send_message(name, nod, trans_data, True)
					if status == False:
						unsynced.append(nod)	
				except:
					unsynced.append(nod)
				
			return unsynced
		else:
			unsync_b_data = self.prepare_data(name, node, witness, txt, unsync, 12)
			for node in xrange(1, self.total_nodes  + 1):
				if node not in unsync:
					status = self.send_message( name, node, unsync_b_data, True)
					if status == False:
						return False

	def active_messaging(self, name, max_msg):
		"""Actively sends out a message to the node requested
		The first line of the message is the node_no to which the message should be sent
		Second line of the message is the actual message to be sent.
		"""
		node = input('Send money to: ')
		if int(node) == n.address:
			print('Cannot send money to yourself')
		else:
			txt = raw_input('Amount: ')
			i = 1
			for trans in n.transaction_history:
				if n.transaction_history[trans].receiver == n.address:
					print 'id: ',
					print n.transaction_history[trans].ID,
					print 'amount: ',
					print n.transaction_history[trans].amount,
					print 'spent',
					print(n.transaction_history[trans].spent)
					i+=1
			ref = raw_input('Reference ids to the transaction: ')
			try:
				ref = ref.split(',')
			except:
				ref = [ref]
			if self.get_seller_agreement(name, node, txt, ref): 
				witness = input('Witness: ')
				if (int(witness) == n.address) or (int(witness) == int(node)):
					print('Invalid Witness!')
				else:
					if witness == 'random':
						witness = self.get_witness(name, node, txt, ref)
					if self.send_witness(name, node, witness, txt,ref):
						for trans in ref:
							money_in = 0
							try:
								x = n.transaction_history[trans]
								if x.receiver == sender:
									if not x.spent:
										money_in += x.amount
							except:
								pass
						a,b = n.create_trans_id(money_in-int(txt))
						unsynced = self.send_to_all(name, node, witness, txt, a,b, reference = ref,m_type = 7)
						if len(unsynced):
							unsync_b_status = self.send_to_all(name, node, witness, txt, a,b,unsynced, 12)
					else: 
						print("no response by witness")
		# self.send_message( name, node, txt)
		max_msg -= 1

	def send_message(self, name, node_no, message, receive = False):
		"""Creates a connection to required node_no, and sends the specified message
		Outputs the same on the screen for logging, etc.
		Args:
			name: Thread name to be printed before printing the message
			node_no: Node to which an incoming connection request must be sent
			message: Message as a text which needs to be sent to the node
		"""
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		host = n.address_stored[node_no]["ip"]
		port = n.address_stored[node_no]["port"]
		try:
			s.connect((host, port))
			s.sendall(message)
		except:
			pass
		if receive:
			data =  s.recv(1024)
			mss_reply = json.loads(data)
			n.message_log.append(data)
			sent_time = mss_reply["time"]
			updated_time = max(sent_time+1, n.l_clock)
			n.l_clock = updated_time+1
			if mss_reply["message_id"] == 2:
				n.convert(mss_reply["transactions"])
				return True
			if mss_reply["message_id"] == 5 or mss_reply["message_id"] == 11:
				return True
			elif mss_reply["message_id"] == 6:
				return False
			elif mss_reply["message_id"] == 13:
				# got a request to send the public key on the current node
				s.sendall(self.prepare_data(m_type = 9))
				# sent the public key to the peer
				data = s.recv(1024)
				mss_reply = json.loads(data)
				#got the status of the broadcast from the peer
				if mss_reply["message_id"] == 5 or mss_reply["message_id"] == 11:
					return True
				elif mss_reply["message_id"] == 6:
					return False
			return False

		s.close()


class Passive(threading.Thread, Data):
	"""Waits for incoming connections to the specified port
	Prints the message received to standard output
	"""
	def __init__(self, name, node_no, dht):
		threading.Thread.__init__(self)
		self.name = name
		self.node = node_no
		self.dht = dht

	def run(self):
		self.passive_messaging( self.name, self.node, 100)

	def passive_messaging(self, name, node_no, max_req):
		"""Waits for incoming connections and prints the messages on terminal
		Args:
			name: Thread name to be printed before the message
			node_no: Node no for this node, to bind the socket to this port
			max_req: Maximum number of messages to receive before closing this thread
		"""
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			host = n.ip_address
			port = n.port
			s.bind((host, port))
			s.listen(max_req)
			while(n.online):
				soc,addr = s.accept()
				data = soc.recv(1024)
				data_dict = json.loads(data)
				n.message_log.append(data)
				ret = self.manage_data(node_no,data_dict,soc)
				soc.sendall(ret)
				soc.close()
			s.close()
		except: pass
# Initialising

current_node = int(sys.argv[1]) #Command line argument to denote which node_no this is
n = nt.Node(current_node)
node_name = current_node

active_name = node_name
passive_name = node_name

#create a DHT for getting the public keys
total_nodes = 75
dht = DHT(total_nodes)
dht.insert(current_node)

# Create thread objects
p = Passive(passive_name, current_node, dht)
a = Active(active_name, current_node, dht)

# When nodes comes online
p.start()
for nodes in range(total_nodes):
	nodes+=1
	try:
		if nodes == n.address: continue
		if a.send_message(n.address, int(nodes), Data().prepare_data(m_type = 1), receive = True):# receive message of type 2
			break
		else: print("why??")
	except:
		pass

while n.online:
	if n.online:
		choice = int(raw_input('For initiating a transaction press 1\nFor going offline press 2\nFor message log press 3\nTo Check available balance press 4\nFor self transaction history press 5\nTo see all transactions press 6\nTo go to commits window press 7\n'))
		if choice == 1:
			a.active_messaging(active_name,10)
		elif choice == 2:
			n.Offline()
			a.send_message(n.address, n.address,'Going Offline...')
		elif choice ==3:
			for message in n.message_log:
				print(message +'\n')
		elif choice ==4:
			print('Available Balance: '+ str(n.check_balance()))
		elif choice == 5:
			i = 0
			for trans in n.transaction_history:
				if n.transaction_history[trans].receiver == n.address:
					print 'id: ',
					print n.transaction_history[trans].ID,
					print 'amount: ',
					print n.transaction_history[trans].amount,
					print 'spent',
					print(n.transaction_history[trans].spent)
					i+=1
		elif choice== 6:
			i = 0
			for trans in n.transaction_history:
				print 'id: ',
				print n.transaction_history[trans].ID,
				print 'from: ',
				print n.transaction_history[trans].initiator,
				print 'to: ',
				print n.transaction_history[trans].receiver,
				print 'witness: ',
				print n.transaction_history[trans].witness,
				print 'amount: ',
				print n.transaction_history[trans].amount,
				print 'spent',
				print(n.transaction_history[trans].spent)
				i+=1
		elif choice == 7:
			time.sleep(10)




























