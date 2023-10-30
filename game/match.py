from .game import newBallPosition
import math
import random

gamedata = {}

def getAngle(turn):
	if(turn == 'a'):
		return random.randint(135, 225)
	else:
		return random.randint(315, 405) % 360

def setupGameLoop(match_name):
	global gamedata
	rand = random.randint(0, 1)
	turn = 'b'
	if(rand == 0):
		turn = 'a'
	gamedata[match_name] = {}
	gamedata[match_name]['ballY'] = 300 + 10
	gamedata[match_name]['ballX'] = 400 - 10
	gamedata[match_name]['ballRad'] = math.radians(getAngle(turn))
	gamedata[match_name]['ballVelocity'] = 5
	gamedata[match_name]['scoreA'] = 0
	gamedata[match_name]['scoreB'] = 0
	gamedata[match_name]['turn'] = turn
	gamedata[match_name]['sound'] = 'none'

def gameloop(match_name, data):
	global gamedata
	gamedata[match_name]['aY'] = data['aY']
	gamedata[match_name]['bY'] = data['bY']

	gamedata[match_name] = newBallPosition(
		gamedata[match_name]['aY'], gamedata[match_name]['bY'],
		gamedata[match_name]['ballY'], gamedata[match_name]['ballX'], gamedata[match_name]['ballRad'], gamedata[match_name]['ballVelocity'],
		gamedata[match_name]['scoreA'], gamedata[match_name]['scoreB'], gamedata[match_name]['turn'])
	return gamedata[match_name]