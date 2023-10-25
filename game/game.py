import math

leftShift = 400
aX = leftShift + 35
bX = leftShift + 745
paddleSize = 100
topWall = 20
botWall = 600
middleX = 400 - 10 + leftShift
middleY = 300 + 10

#garanta que só bata 1 vez a bola por paddle
def newBallPosition(aY, bY, ballY, ballX, ballRad, ballVelocity, scoreA, scoreB, turn):
	
	
	sound = "none"
	#bot
	if(ballY >= 570):
		bY = 520
	elif(ballY <= 70):
		bY = 20
	else:
		bY = ballY - 50
	# print(aY, bY, ballX, ballY, ballVelocity)
	
	ballX += ballVelocity * math.cos(ballRad)
	ballY += ballVelocity * math.sin(ballRad)
	#ball went off limits
	if (ballX < leftShift or ballX > leftShift + 800):
		if(ballX < leftShift):
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
			ballRad = math.radians(60)
		elif (ballY < aY + 25):
			ballRad = math.radians(300)
		else:
			ballRad = math.radians(180) - ballRad
		if(ballVelocity < 10):
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
		if(ballVelocity < 10):
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
		'sound':sound
	})
