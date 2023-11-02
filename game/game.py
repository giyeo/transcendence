import math
import random
import time

aX = 35
bX = 745
paddleSize = 100
topWall = 20
botWall = 600
middleX = 400 - 10
middleY = 300 + 10
change = True
execs = 0

#garanta que só bata 1 vez a bola por paddle
def newBallPosition(aY, bY, ballY, ballX, ballRad, ballVelocity, scoreA, scoreB, turn, gamemode):
	global paddleSize, execs
	
	execs += 1
	if(gamemode == 'crazyPaddleSizes' and execs % (90 * 3) == 0):
		paddleSize = random.choice([100, 150])
	sound = "none"
	#bot
	# if(ballY >= 570):
	# 	bY = 520
	# elif(ballY <= 70):
	# 	bY = 20
	# else:
	# 	bY = ballY - 50
	
	# print(aY, bY, ballX, ballY, ballVelocity)

	ballX += ballVelocity * math.cos(ballRad)
	ballY += ballVelocity * math.sin(ballRad)

	#ball went off limits
	if (ballX < 0 or ballX > 800):
		if(ballX < 0):
			scoreB += 1
			ballX = bX - 20
		else:
			scoreA += 1
			ballX = aX + 20
		ballY = middleY
		ballVelocity = 5
		sound = "score"

	#hit paddle A
	if (turn == 'a'
	and (ballY > aY - 20 and ballY < aY + paddleSize)
	and (ballX > aX - 20 and ballX < aX + 20) ):
		if(ballY > aY + 75):
			ballRad = math.radians(60 - random.randint(0, 30))
		elif (ballY < aY + 25):
			ballRad = math.radians(300 + random.randint(0, 30))
		else:
			ballRad = math.radians(180) - ballRad
		if(ballVelocity < 20):
			ballVelocity += 0.25
		turn = 'b'
		sound = "paddle"
	#hit paddle B
	if (turn == 'b'
	and (ballY > bY - 20 and ballY < bY + paddleSize)
	and (ballX > bX - 20 and ballX < bX + 20) ):
		if(ballY > bY + 75):
			ballRad = math.radians(150)
		elif (ballY < bY + 25):
			ballRad = math.radians(225)
		else:
			ballRad = math.radians(180) - ballRad
		if(ballVelocity < 20):
			ballVelocity += 0.25
		turn = 'a'
		sound = "paddle"

	#hit wall
	if (ballY <= topWall or ballY >= botWall):
		ballRad = -ballRad
		sound = "wall"
	return ({
		'aY':aY,
		'bY':bY,
		'ballY':ballY,
		'ballX':ballX,
		'ballRad':ballRad,
		'ballVelocity':ballVelocity,
		'scoreA':scoreA,
		'scoreB':scoreB,
		'turn':turn,
		'sound':sound,
		'paddleSize':paddleSize
	})
