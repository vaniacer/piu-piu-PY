# -*- encoding: utf-8 -*-
"""
Модуль клиента.
"""

import socket
import pickle

class ClientClass:

	def __init__(self, localhero, remotehero, enemy, boss, host='localhost', port=9999):
		self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.clientsocket.connect((host, port))
		self.clientsocket.setblocking(False)

		self.localhero  = localhero
		self.remotehero = remotehero
		self.enemy = enemy
		self.boss  = boss

		self.remotehero_data   = (10, 10, 0, 0, 3, 100, 7, 1000)
		self.localhero_data_in = (0, 3, 100, 7, 1000)
		self.enemy_data = ()
		self.boss_data  = ()

		self.data_in   = ()
		self.data_out  = ()

		self.server_addr = (host, port)

	def receive(self):

		try:

			self.data_in, self.addr = self.clientsocket.recvfrom(297)
			self.remote_data = pickle.loads(self.data_in) #Unpickle the data

			self.remotehero_data, self.localhero_data_in, self.enemy_data, self.boss_data = self.remote_data

		except socket.error, err:

			#print err
			pass


	def send(self):

		self.localhero_data = (self.localhero.x, self.localhero.y, self.localhero.fire)
		self.data_out = (self.localhero_data)

		self.clientsocket.sendto(pickle.dumps(self.data_out), self.server_addr)
