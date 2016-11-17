#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import pygame
import sys
import random
import Server
import Client
import inputbox
from pygame.locals import *

pygame.init()

FPS      = 60 # frames per second setting
fpsClock = pygame.time.Clock()


# set up the window
pygame.display.set_caption('Piu Piu!')

WX = 400
WY = 300

WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
BACK  = (138, 174, 195)
RED   = (255,   0,   0)

FONT      = pygame.font.Font('freesansbold.ttf', 16)
BIGFONT   = pygame.font.Font('freesansbold.ttf', 32)
SCREEN    = pygame.display.set_mode((WX, WY), 0, 32)


# load sprites
bosssurf  = [pygame.image.load(os.path.join('boss',  '%d%s' % (x, '.png'))) for x in range(1,5)]
blastsurf = [pygame.image.load(os.path.join('blast', '%d%s' % (x, '.png'))) for x in range(1,6)]
herosurf  = pygame.image.load('plane.png')
enemysurf = pygame.image.load('enemy.png')
bullet    = pygame.image.load('bullet.png')
bbullet   = pygame.transform.scale(pygame.transform.flip(bullet,  True, False), (30, 30))

firep     = pygame.image.load('firepower.png')
firer     = pygame.image.load('firerate.png')
ammo      = pygame.image.load('ammo.png')
life      = pygame.image.load('life.png')
bonus     = (firep, firer, ammo, life)

ground    = pygame.image.load('back.png')
cloudsl   = pygame.image.load('clouds.png')
cloudst   = pygame.transform.flip(cloudsl, False, True)

#Text
gameOverSurf        = FONT.render('Game Over!', True, RED)
gameOverRect        = gameOverSurf.get_rect()
gameOverRect.center = (WX / 2, WY / 2 - 10)

gameWinSurf         = FONT.render('WELL DONE!', True, RED)
gameWinRect         = gameWinSurf.get_rect()
gameWinRect.center  = (WX / 2, WY / 2 - 10)

PiuPiuSurf          = BIGFONT.render('Piu-Piu!', True, RED)
PiuPiuRect          = PiuPiuSurf.get_rect()
PiuPiuRect.center   = (WX / 2, WY / 2 - 10)

# get alpha copy of hero plane
herosurfa = herosurf.copy()
alpha = 128
herosurfa.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

# get rotated copy of hero plane
herosurfr = pygame.transform.rotate(herosurf, -45)

# show rects
showrect = False

# server\client
server 	    = False
client      = False
server_addr = 'localhost'

# God mode
godmode  = False

def MX():
	x, y = pygame.mouse.get_pos()

	return x


def MY():
	x, y = pygame.mouse.get_pos()

	return y


class BossClass(pygame.sprite.Sprite):
	"""class for boss enemy"""

	def __init__(self):
		super(BossClass, self).__init__()
		self.cooldown  = 100
		self.cooldownt = 0
		self.bornt     = 0
		self.timer     = 0
		self.blastst   = 0
		self.loop      = 0
		self.width     = 80
		self.height    = 38
		self.direction = 1
		self.health    = 10000
		self.x         = WX + self.width
		self.y         = 0

		if server or client:

			self.health = 20000


	def update(self):

		global endgame

		# image animation
		if pygame.time.get_ticks() - self.timer >= 100 and self.health > 0:
			self.timer = pygame.time.get_ticks()

			if self.loop < len(bosssurf) - 1:
				self.loop += 1
			else:
				self.loop  = 0

		# movement
		if self.x > 250 and self.health > 0:
			self.x -= self.direction

			if self.x < 260:
				self.direction = -1

			if self.x > 320:
				self.direction = 1
		else:
			self.x -= 1

			if self.x < -90:
				endgame = 'win'

		if not server and not client:

			if self.y > MY() and self.health > 0 and localhero.health > 0:
				self.y -= 1

			elif self.y < MY() and self.health > 0 and localhero.health > 0:
				self.y += 1

			elif self.y == MY() and self.health > 0 and localhero.health > 0:
				bossfire()

		else:

			# check dist to heroes
			self.torem = abs(self.y - remotehero.y)
			self.toloc = abs(self.y - localhero.y)

			# go to local hero
			if self.toloc < self.torem and localhero.health > 0 and self.health > 0:

				if self.y > localhero.y:

					self.y -= 1

				elif self.y < localhero.y:

					self.y += 1

				elif self.y == localhero.y:

					bossfire()

			# go to remote hero
			elif self.torem < self.toloc and remotehero.health > 0 and self.health > 0:

				if self.y > remotehero.y:

					self.y -= 1

				elif self.y < remotehero.y:

					self.y += 1

				elif self.y == remotehero.y:

					bossfire()

		if self.health <= 0 and self.y < WY - self.height:
			self.y += 1

		if client:

			self.x, self.y, self.health = client.boss_data

		if self.health <= 0 and pygame.time.get_ticks() - self.blastst >= 200:
			self.blastst = pygame.time.get_ticks()
			a = random.randrange(1, 70) - 20
			b = random.randrange(1, 30) - 20
			blastgroup.add(BlastClass(self.x + a, self.y + b, 1))

		self.image = bosssurf[self.loop]
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		#self.rect = pygame.Rect(200, 150, self.width, self.height)
		if showrect == True:
			pygame.draw.rect(SCREEN, RED, self.rect, 1)


class LocalHeroClass(pygame.sprite.Sprite):
	"""class for our hero"""

	def __init__(self):
		super(LocalHeroClass, self).__init__()
		self.cooldown  = 100
		self.enmkiled  = 0
		self.cooldownt = 0
		self.blastst   = 0
		self.fallt     = 0
		self.falls     = 1
		self.fire      = 0
		self.firepower = 7
		self.timer     = 0
		self.loop      = 0
		self.rotate    = 0
		self.health    = 3
		self.width     = 40
		self.height    = 40
		self.ammobox   = 1000
		self.collided  = False
		self.image     = herosurf
		self.x, self.y = -30, -30

	def update(self):

		global endgame

		#print 'local', self.firepower

		if client:

			self.enmkiled, \
			self.health, \
			self.cooldown, \
			self.firepower, \
			self.ammobox = client.localhero_data_in

		if self.health > 0:
			self.x, self.y = pygame.mouse.get_pos()

		elif self.y < WY - self.height:

			if self.rotate != -45:
				self.rotate -= 1
				self.image   = pygame.transform.rotate(herosurf, self.rotate)

			if pygame.time.get_ticks() - self.fallt >= 35:
				self.fallt = pygame.time.get_ticks()
				self.y     += self.falls
				self.x     += 1
				self.falls += 1

		elif self.y > WY - self.height:
			self.y = WY - self.height

		elif self.x > -50:
			self.x -= 1

		else:

			if client or server:

				if remotehero.health <= 0:

					endgame = 'loose'

			else:
				endgame = 'loose'

		if self.health <= 0 and pygame.time.get_ticks() - self.blastst >= 300:
			#self.image   = herosurfr
			self.blastst = pygame.time.get_ticks()
			a = random.randrange(1, 20) - 10
			b = random.randrange(1, 20) - 10
			blastgroup.add(BlastClass(self.x + a, self.y + b, 1))

		if self.collided == True and self.health > 0 and pygame.time.get_ticks() - self.timer >= 100:
			self.timer = pygame.time.get_ticks()

			if self.loop < 5:
				self.loop += 1
				if self.image == herosurf:
					self.image = herosurfa

				elif self.image == herosurfa:
					self.image = herosurf

			else:
				self.loop     = 0
				self.collided = False
				self.image    = herosurf

		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		if showrect == True:
			pygame.draw.rect(SCREEN, RED, self.rect, 1)


class RemoteHeroClass(pygame.sprite.Sprite):
	"""class for our remote hero"""

	def __init__(self):
		super(RemoteHeroClass, self).__init__()
		self.cooldown  = 100
		self.enmkiled  = 0
		self.cooldownt = 0
		self.blastst   = 0
		self.fallt     = 0
		self.falls     = 1
		self.fire      = 0
		self.firepower = 7
		self.timer     = 0
		self.loop      = 0
		self.rotate    = 0
		self.health    = 3
		self.width     = 40
		self.height    = 40
		self.ammobox   = 1000
		self.collided  = False
		self.image     = herosurf
		self.x, self.y = -30, -30


	def update(self):

		global endgame

		#print 'remote', self.firepower

		if self.health > 0:

			if server:

				self.x, \
				self.y, \
				self.fire = server.remotehero_data

			if client:

				self.x, \
				self.y, \
				self.enmkiled, \
				self.fire, \
				self.health, \
				self.cooldown, \
				self.firepower, \
				self.ammobox  = client.remotehero_data

		elif self.y < WY - self.height:

			if self.rotate != -45:
				self.rotate -= 1
				self.image   = pygame.transform.rotate(herosurf, self.rotate)

			if pygame.time.get_ticks() - self.fallt >= 35:
				self.fallt = pygame.time.get_ticks()
				self.y     += self.falls
				self.x     += 1
				self.falls += 1

		elif self.y > WY - self.height:
			self.y = WY - self.height

		elif self.x > -50:
			self.x -= 1

			if client or server:

				if localhero.health <= 0:

					endgame = 'loose'

			else:
				endgame = 'loose'

		if self.health <= 0 and pygame.time.get_ticks() - self.blastst >= 300:
			#self.image   = herosurfr
			self.blastst = pygame.time.get_ticks()
			a = random.randrange(1, 20) - 10
			b = random.randrange(1, 20) - 10
			blastgroup.add(BlastClass(self.x + a, self.y + b, 1))

		if self.collided == True and self.health > 0 and pygame.time.get_ticks() - self.timer >= 100:
			self.timer = pygame.time.get_ticks()

			if self.loop < 5:
				self.loop += 1
				if self.image == herosurf:
					self.image = herosurfa

				elif self.image == herosurfa:
					self.image = herosurf

			else:
				self.loop     = 0
				self.collided = False
				self.image    = herosurf

		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		if showrect == True:
			pygame.draw.rect(SCREEN, RED, self.rect, 1)


class EnemyClass(pygame.sprite.Sprite):
	"""class for enemies"""

	def __init__(self, id):
		super(EnemyClass, self).__init__()
		self.id     = id
		self.timer  = 0
		self.loop   = 0
		self.born   = 0
		self.width  = 40
		self.height = 40
		self.bonus  = (random.randrange(0, 4), random.randrange(0, 2))
		self.health = enmyhealth
		self.image  = enemysurf
		self.x, self.y = 500, 200

		if not client:

			if not bosshow:

				self.x, self.y = random.randrange(450, 500), random.randrange(10, 250)

			else:
				self.x, self.y = boss.x + 20, boss.y + 18
				self.born      = self.y + 30
				if self.born  >= 280:
					self.born  = 280

		else:

			for data in client.enemy_data:

					if self.id == data[0]:

						self.x, self.y, self.health, self.bonus = data[1:]


	def client_load(self):

		for data in client.enemy_data:

				if self.id == data[0]:

					self.x, self.y, self.health, self.bonus = data[1:]


	def update(self):

		global enmyhealth, enmid

		if client:

			self.client_load()

		# movement
		if self.x > -40:

			self.x -= 1

		else:

			enemygroup.remove(self)
			enmid.append(self.id)

		if self.y < self.born:

			self.y += 1

		# rect
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

		if showrect == True:

			pygame.draw.rect(SCREEN, RED, self.rect, 1)


class BossBulletClass(pygame.sprite.Sprite):
	"""class for boss bullets"""

	def __init__(self):
		super(BossBulletClass, self).__init__()
		self.width     = 30
		self.height    = 30
		self.image     = bbullet
		self.x, self.y = boss.x - 32, boss.y + 10

	def update(self):

		# movement
		self.x -= 5

		if self.x < -30:
			bossbgroup.remove(self)

		self.rect      = pygame.Rect(self.x, self.y, self.width, self.height)
		if showrect == True:
			pygame.draw.rect(SCREEN, RED, self.rect, 1)


class HeroBulletClass(pygame.sprite.Sprite):
	"""class for hero bullets"""

	def __init__(self, x, y, local):
		super(HeroBulletClass, self).__init__()
		self.x, self.y = x, y
		self.local = local
		self.width = 30
		self.x    += 32

		if self.local:

			self.y += 20 - localhero.firepower / 2

		else:

			self.y += 20 - remotehero.firepower / 2

	def update(self):

		# movement
		self.x += 10

		if self.x > WX:
			herobgroup.remove(self)

		if self.local:

			self.image     = pygame.transform.scale(bullet, (self.width, localhero.firepower))
			self.rect      = pygame.Rect(self.x, self.y, self.width, localhero.firepower)

		else:

			self.image     = pygame.transform.scale(bullet, (self.width, remotehero.firepower))
			self.rect      = pygame.Rect(self.x, self.y, self.width, remotehero.firepower)

		if showrect == True:

			pygame.draw.rect(SCREEN, RED, self.rect, 1)


class BonusClass(pygame.sprite.Sprite):
	"""class for bonuses"""

	def __init__(self, X, Y, num):
		super(BonusClass, self).__init__()
		self.width     = 40
		self.height    = 40
		self.x, self.y = X, Y
		self.image     = bonus[num]

	def update(self):
		# movement
		self.x -= 1

		if self.x < -40:
			bonusgroup.remove(self)

		self.rect      = pygame.Rect(self.x, self.y, self.width, self.height)
		if showrect == True:
			pygame.draw.rect(SCREEN, RED, self.rect, 1)


class BlastClass(pygame.sprite.Sprite):
	"""class for blasts"""

	def __init__(self, x, y, bossy):
		super(BlastClass, self).__init__()
		self.timer     = 0
		self.loop      = 0
		self.width     = 40
		self.height    = 40
		self.bossy     = bossy
		self.x, self.y = x, y

	def update(self):
		# image animation
		if pygame.time.get_ticks() - self.timer >= 30:
			self.timer = pygame.time.get_ticks()

			if self.loop < len(blastsurf) - 1:
				self.loop += 1
			else:
				blastgroup.remove(self)
				self.loop  = 0

		# movement
		self.x -= 1

		if self.bossy != 0:
			self.y += 1

		if self.x < -40:
			blastgroup.remove(self)

		self.image = blastsurf[self.loop]
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		if showrect == True:
			pygame.draw.rect(SCREEN, RED, self.rect, 1)


class BackgroundClass(pygame.sprite.Sprite):
	"""class for background"""

	def __init__(self, surf, pause, X, Y):
		super(BackgroundClass, self).__init__()
		self.timer     = 0
		self.width     = 40
		self.height    = 40
		self.pause     = pause
		self.x, self.y = X, Y
		self.image     = surf

	def update(self):
		# movement
		if pygame.time.get_ticks() - self.timer >= self.pause:
			self.timer = pygame.time.get_ticks()
			self.x -= 1

			if self.x == -400:
				self.x = 0

			self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
			if showrect == True:
				pygame.draw.rect(SCREEN, RED, self.rect, 1)


class ButtonClass:
	"""class for buttons"""

	def __init__(self, text, color, yshift, func):
		self.image       = FONT.render(text, True, color)
		self.rect        = self.image.get_rect()
		self.rect.center = (WX / 2, WY / 2 + yshift)
		self.func        = func
		self.enabled     = False

	def update(self):
		# on press
		SCREEN.blit(self.image, self.rect)

		if self.enabled:

			if self.rect.collidepoint(pygame.mouse.get_pos()):
				if pygame.mouse.get_pressed()[0]:
					self.func()


def bossfire():
	if pygame.time.get_ticks() - boss.cooldownt >= boss.cooldown:
		boss.cooldownt = pygame.time.get_ticks()
		bossbgroup.add(BossBulletClass())


def herofire():

	localhero.fire = pygame.mouse.get_pressed()[0]

	if pygame.mouse.get_pressed()[0] and localhero.ammobox > 0 and localhero.health > 0:

		if pygame.time.get_ticks() - localhero.cooldownt >= localhero.cooldown:
			localhero.cooldownt = pygame.time.get_ticks()
			herobgroup.add(HeroBulletClass(localhero.x, localhero.y, True))
			localhero.ammobox -= 1

	if server or client:

		if remotehero.fire and remotehero.ammobox > 0 and remotehero.health > 0:

			if pygame.time.get_ticks() - remotehero.cooldownt >= remotehero.cooldown:
				remotehero.cooldownt = pygame.time.get_ticks()
				herobgroup.add(HeroBulletClass(remotehero.x, remotehero.y, False))
				remotehero.ammobox -= 1


def bosscollide():
	if boss.health > 0:

		hit = pygame.sprite.spritecollideany(boss, herogroup, collided = None)

		if hit:

			if pygame.sprite.collide_mask(hit, boss):

				if not hit.collided:

					boss.health  -= 100
					hit.collided = True

					if not godmode:

						hit.health  -= 1



	hit = pygame.sprite.spritecollideany(boss, herobgroup, collided = None)

	if hit:

		if pygame.sprite.collide_mask(hit, boss):

			herobgroup.remove(hit)

			if hit.local:

				boss.health -= localhero.firepower

			else:

				boss.health -= remotehero.firepower


def herocollide():

	hit = pygame.sprite.groupcollide(herogroup, bossbgroup, False, False, collided = None)

	if hit:

		for hero, bullets in hit.items():

			for bul in bullets:

				if pygame.sprite.collide_mask(hero, bul):

					if not client:

						if not godmode:

							hero.health -= 1

					bossbgroup.remove(bul)

	hit = pygame.sprite.groupcollide(herogroup, bonusgroup, False, False, collided = None)

	if hit:

		for hero, bonus in hit.items():

			for spr in bonus:

				if pygame.sprite.collide_mask(hero, spr):

					if not client:

						if spr.image == life:
							hero.health += 1

						elif spr.image == ammo:
							hero.ammobox += 200

						elif spr.image == firep:
							hero.firepower += 1

						elif spr.image == firer:
							hero.cooldown -= 1

					bonusgroup.remove(spr)


def enemycollide():

	#hit = pygame.sprite.spritecollideany(hero, enemygroup, collided = None)
	hit = pygame.sprite.groupcollide(herogroup, enemygroup, False, False, collided = None)

	if hit:

		for hero, enemies in hit.items():

			for en in enemies:

				if pygame.sprite.collide_mask(hero, en):

					hero.collided = True

					if not client:

						if not godmode:

							hero.health  -= 1

						hero.enmkiled += 1
						en.health   = 0

	hit = pygame.sprite.groupcollide(enemygroup, herobgroup, False, False, collided = None)

	if hit:

		for enemy, bullets in hit.items():

			for bul in bullets:

				if pygame.sprite.collide_mask(enemy, bul):

					if not client:

						enemy.health -= localhero.firepower

						if enemy.health < 0:

							if bul.local:

								localhero.enmkiled += 1

							else:

								remotehero.enmkiled += 1

					herobgroup.remove(bul)


def bossHealthMeter():
	bossurf  = FONT.render('BOSS: ', True, RED)
	bossrect = bossurf.get_rect()

	hm       = WX - bossrect[2] - 5 * 2
	health   = boss.health / 100

	if health < 0:
		health = 0

	hp      = float(hm) / 100 * health
	boshm   = pygame.Surface((hp, 16))
	boshm.fill((RED))
	boshm.set_alpha(150)

	SCREEN.blit(bossurf, (5, 280))
	SCREEN.blit(boshm, (bossrect[2] + 5, 281))


def makenemy():

	global enmid

	if len(enemygroup) < maxenemy:

		if not bosshow:

			enemygroup.add(EnemyClass(enmid[0]))
			del enmid[0]

		if bosshow and boss.health > 0 and pygame.time.get_ticks() - boss.bornt >= 1000:

			boss.bornt = pygame.time.get_ticks()
			enemygroup.add(EnemyClass(enmid[0]))
			del enmid[0]


def cakemake():

	global enmyhealth

	for en in enemygroup:

		if en.health <= 0:

			if en.bonus[1] == 0:
				bonusgroup.add(BonusClass(en.x, en.y, en.bonus[0]))

			blastgroup.add(BlastClass(en.x, en.y, 0))
			enemygroup.remove(en)
			enmid.append(en.id)
			enmyhealth += 1


def gameinfo():
	# info
	info = [''.join(map(str, ["Local Hero Life: ", localhero.health, " Ammo: ", localhero.ammobox, "  Enemy Kiled: ", localhero.enmkiled]))]
	gameInfoSurf = FONT.render("".join(info), True, WHITE)
	SCREEN.blit(gameInfoSurf, (5, 5))

	if server or client:

		info2 = [''.join(map(str, ["Remote Hero Life: ", remotehero.health, " Ammo: ", remotehero.ammobox, "  Enemy Kiled: ", remotehero.enmkiled]))]
		gameInfo2Surf = FONT.render("".join(info2), True, WHITE)
		SCREEN.blit(gameInfo2Surf, (5, 20))


def startServer():

	global server
	server = True
	startGame()


def startClient():

	global client
	client = True
	startGame()


def startGame():

	global server, client, enmid, maxenemy, tillboss, enmyhealth, endgame, bosshow, enmyhealth, localhero, \
		remotehero, boss, enemygroup, herogroup, herobgroup, bossbgroup, blastgroup, bonusgroup

	bosshow    = False
	endgame    = 'game'
	maxenemy   = 5
	tillboss   = 100
	enmyhealth = 100

	boss = BossClass()
	localhero = LocalHeroClass()

	herogroup  = pygame.sprite.Group(localhero)

	bossgroup  = pygame.sprite.Group(boss)
	herobgroup = pygame.sprite.Group()
	bossbgroup = pygame.sprite.Group()
	enemygroup = pygame.sprite.Group()
	blastgroup = pygame.sprite.Group()
	bonusgroup = pygame.sprite.Group()

	if server or client:

		tillboss   = 200
		remotehero = RemoteHeroClass()
		herogroup.add(remotehero)

	if server:

		server = Server.ServerClass(localhero, remotehero, enemygroup, boss)

	if client:

		client = Client.ClientClass(localhero, remotehero, enemygroup, boss, server_addr)

	pygame.mouse.set_visible(0)

	enmid = []

	for i in range(maxenemy):

		enmid.append(i)

	while True: #---------------------------------------- main game loop -----------------------------------------------
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

		makenemy()
		herofire()

		# fill screen
		SCREEN.fill(BACK)

		# update & draw sprites
		bgroundgroup.update()
		bgroundgroup.draw(SCREEN)

		enemygroup.update()
		enemygroup.draw(SCREEN)

		bonusgroup.update()
		bonusgroup.draw(SCREEN)

		herobgroup.update()
		herobgroup.draw(SCREEN)
		herogroup.update()
		herogroup.draw(SCREEN)

		if bosshow == True:
			bossgroup.update()
			bossbgroup.update()
			bossgroup.draw(SCREEN)
			bossbgroup.draw(SCREEN)

			bossHealthMeter()
			bosscollide()

		blastgroup.update()
		blastgroup.draw(SCREEN)

		gameinfo()

		enemycollide()
		herocollide()

		if client or server:

			if localhero.enmkiled + remotehero.enmkiled > tillboss:
				bosshow = True

		else:

			if localhero.enmkiled > tillboss:
				bosshow = True

		if endgame == 'win':
			gameover(True)

		elif endgame == 'loose':
			gameover(False)

		# Server
		if server:

			server.receive()
			server.send()

		# Client
		elif client:

			client.receive()
			client.send()

		cakemake()

		pygame.display.update()
		fpsClock.tick(FPS)


def gameover(win):

	A           = 0
	darktimer   = 0
	buttontimer = pygame.time.get_ticks()
	darkness   = pygame.Surface((WX, WY))

	darkness.fill((BLACK))
	darkness.set_alpha(A)

	pygame.mouse.set_visible(1)

	again = ButtonClass("again", WHITE, 30, startGame)
	back  = ButtonClass("menu",  WHITE, 60, menu)
	exit  = ButtonClass("exit",  WHITE, 90, sys.exit)

	while True:

		for event in pygame.event.get():

			if event.type == QUIT:

				pygame.quit()
				sys.exit()

		if pygame.time.get_ticks() - darktimer >= 500:

			darktimer = pygame.time.get_ticks()

			if A != 255:

				A += 1
			darkness.set_alpha(A)
			SCREEN.blit(darkness, (0, 0))

		if win == False:

			SCREEN.blit(gameOverSurf, gameOverRect)

		else:

			SCREEN.blit(gameWinSurf, gameWinRect)

		again.update()
		back.update()
		exit.update()

		if pygame.time.get_ticks() - buttontimer >= 500:

			buttontimer = pygame.time.get_ticks()
			again.enabled = True
			back.enabled = True
			exit.enabled = True


		pygame.display.update()
		fpsClock.tick(FPS)

def clientMenu():

	global server_addr

	buttontimer = pygame.time.get_ticks()
	pygame.mouse.set_visible(1)

	start    = ButtonClass("Start", WHITE,  90, startClient)
	exit      = ButtonClass("exit",   WHITE, 120, sys.exit)

	SCREEN.fill(BLACK)

	start.update()
	exit.update()

	inputbox.display_box(SCREEN,'')
	server_addr = inputbox.ask(SCREEN, 'Enter Server Adress')

	EntrServer          = BIGFONT.render(server_addr, True, RED)
	EntSrvRect          = EntrServer.get_rect()
	EntSrvRect.center   = (WX / 2, WY / 2 - 10)

	while True:

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

		SCREEN.fill(BLACK)
		SCREEN.blit(EntrServer, EntSrvRect)

		start.update()
		exit.update()

		if pygame.time.get_ticks() - buttontimer >= 500:

			buttontimer = pygame.time.get_ticks()

			start.enabled = True
			exit.enabled = True

		pygame.display.update()
		fpsClock.tick(FPS)


def menu():

	buttontimer = pygame.time.get_ticks()
	pygame.mouse.set_visible(1)


	singlplay = ButtonClass("Single", WHITE,  30, startGame)
	server    = ButtonClass("Server", WHITE,  60, startServer)
	client    = ButtonClass("Client", WHITE,  90, clientMenu)
	exit      = ButtonClass("exit",   WHITE, 120, sys.exit)

	while True:

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

		SCREEN.fill(BLACK)
		SCREEN.blit(PiuPiuSurf, PiuPiuRect)

		singlplay.update()
		server.update()
		client.update()
		exit.update()

		if pygame.time.get_ticks() - buttontimer >= 1000:

			buttontimer = pygame.time.get_ticks()
			singlplay.enabled = True
			server.enabled = True
			client.enabled = True
			exit.enabled = True

		pygame.display.update()
		fpsClock.tick(FPS)

cloudslow    = BackgroundClass(cloudsl, 50, 0, 210)
cloudstop    = BackgroundClass(cloudst, 30, 0,   0)
earth        = BackgroundClass(ground,  20, 0, 260)
bgroundgroup = pygame.sprite.OrderedUpdates(cloudslow, cloudstop, earth)

menu()
