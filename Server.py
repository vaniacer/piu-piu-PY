# -*- encoding: utf-8 -*-
"""
Модуль сервера.
"""

import socket
import pickle

class ServerClass:

	def __init__(self, localhero, remotehero, enemy, boss, host='', port=9999):
		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.serversocket.bind((host, port))
		self.serversocket.setblocking(False)

		self.localhero  = localhero
		self.remotehero = remotehero
		self.enemy = enemy
		self.boss  = boss

		self.remotehero_data = (10, 10, 0)
		self.enemy_data = ()
		self.boss_data  = ()

		self.data_in   = ()
		self.data_out  = ()

		self.addr  = False


	def receive(self):

		try:

			self.data_in, self.addr = self.serversocket.recvfrom(297)
			self.remote_data = pickle.loads(self.data_in) #Unpickle the data

			self.remotehero_data = (self.remote_data)


		except socket.error, err:

			#print err
			pass


	def send(self):

		# Hero data
		self.localhero_data      = (self.localhero.x,
									self.localhero.y,
									self.localhero.enmkiled,
									self.localhero.fire,
									self.localhero.health,
									self.localhero.cooldown,
									self.localhero.firepower,
									self.localhero.ammobox)

		self.remotehero_data_out = (self.remotehero.enmkiled,
									self.remotehero.health,
									self.remotehero.cooldown,
									self.remotehero.firepower,
									self.remotehero.ammobox)

		# Enemies data
		for en in self.enemy:

			self.endata = (en.id, en.x, en.y, en.health, en.bonus)
			self.enemy_data += (self.endata,)
			#print self.enemy_data

		# Boss data
		self.boss_data = (self.boss.x, self.boss.y, self.boss.health)

		# All data
		self.data_out = (self.localhero_data, self.remotehero_data_out, self.enemy_data, self.boss_data)

		if self.addr:

			self.serversocket.sendto(pickle.dumps(self.data_out), self.addr)

		self.enemy_data = ()

