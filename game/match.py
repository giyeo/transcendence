from .game import newBallPosition
import math
import random

gamedata = {}
leftShift = 400

def getAngle(turn):
	if(turn == 'a'):
		return random.randint(135, 225)
	else:
		return random.randint(315, 405) % 360

def setupGameLoop():
	global gamedata
	rand = random.randint(0, 1)
	turn = 'b'
	if(rand == 0):
		turn = 'a'
	gamedata['ballY'] = 300 + 10
	gamedata['ballX'] = 400 - 10 + leftShift
	gamedata['ballRad'] = math.radians(getAngle(turn))
	gamedata['ballVelocity'] = 5
	gamedata['scoreA'] = 0
	gamedata['scoreB'] = 0
	gamedata['turn'] = turn
	gamedata['sound'] = 'none'

def gameloop(data):
	global gamedata
	gamedata['aY'] = data['aY']
	gamedata['bY'] = data['bY']

	gamedata = newBallPosition(
		gamedata['aY'], gamedata['bY'],
		gamedata['ballY'], gamedata['ballX'], gamedata['ballRad'], gamedata['ballVelocity'],
		gamedata['scoreA'], gamedata['scoreB'], gamedata['turn'])
	return gamedata