from .game import newBallPosition
import math
import random

gamedata = {}

def getAngle(turn):
	if(turn == 'a'):
		angle = random.randint(135, 165)
	else:
		angle = random.randint(315, 375)
	return angle % 360

def setupGameLoop(match_name, matchType):
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
	gamedata[match_name]['paddleSizeA'] = 100
	gamedata[match_name]['paddleSizeB'] = 100
	gamedata[match_name]['gamemode'] = matchType

	if matchType == 'crazyGameMode':
		# set seed
		random.seed(match_name + 'a')
		gamedata[match_name]['paddleSizeA'] = random.randint(50, 200)
		random.seed(match_name + 'b')
		gamedata[match_name]['paddleSizeB'] = random.randint(50, 200)
		gamedata[match_name]['ballVelocity'] = random.randint(10, 15)
		gamedata[match_name]['scoreA'] = random.randint(0, 2)
		gamedata[match_name]['scoreB'] = random.randint(0, 2)


def gameloop(match_name, gamemode, data):
	global gamedata
	gamedata[match_name]['aY'] = data['aY']
	gamedata[match_name]['bY'] = data['bY']

	gamedata[match_name] = newBallPosition(
		gamedata[match_name]['aY'], gamedata[match_name]['bY'],
		gamedata[match_name]['ballY'], gamedata[match_name]['ballX'], gamedata[match_name]['ballRad'], gamedata[match_name]['ballVelocity'],
		gamedata[match_name]['scoreA'], gamedata[match_name]['scoreB'], gamedata[match_name]['turn'], gamedata[match_name]['paddleSizeA'], gamedata[match_name]['paddleSizeB'],
		gamemode)
	return gamedata[match_name]