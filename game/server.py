from .game import newBallPosition
import time
import math

recv = 0
timeA = int(time.time() * 1000)
emits = 0

#create a hashmap or list, that receives the SID as key, to access current gamedata
# preferabble with O(1). like, gamedata[sid].ballY, or something
# that will enable multiclient play our games
gamedata = {}
leftShift = 400

def calcTime(sid):
    global recv, timeA, emits
    recv = recv + 1
    timeB = int(time.time() * 1000)
    if (timeB - timeA >= 1000):
        print(f"sid: {sid} requests/s: {recv}, response/s:{emits}")
        timeA = timeB
        emits = 0
        recv = 0

def gameloop(sid, data):
    global gamedata, emits
    if(gamedata.get(sid) is None):
        gamedata[sid] = {}
        gamedata[sid]['aY'] = data['aY']
        gamedata[sid]['bY'] = data['bY']
        gamedata[sid]['ballY'] = 300 + 10
        gamedata[sid]['ballX'] = 400 - 10 + leftShift
        gamedata[sid]['ballRad'] = math.radians(315)
        gamedata[sid]['ballVelocity'] = 5
        gamedata[sid]['scoreA'] = 0
        gamedata[sid]['scoreB'] = 0
        gamedata[sid]['turn'] = 'b'
    else:
        gamedata[sid]['aY'] = data['aY']
        gamedata[sid]['bY'] = data['bY']

    gamedata[sid] = newBallPosition(
        gamedata[sid]['aY'], gamedata[sid]['bY'],
        gamedata[sid]['ballY'], gamedata[sid]['ballX'], gamedata[sid]['ballRad'], gamedata[sid]['ballVelocity'],
        gamedata[sid]['scoreA'], gamedata[sid]['scoreB'], gamedata[sid]['turn'])
    emits += 1
    calcTime(sid)
    return gamedata[sid]

#if not set in localhost, it get 1000 recv in the front, but in ngrok only 30 recv
#this happens because it only ASKS when it comes, so the backend should send even
#if the front dont asks for it. so, there will be N frames with the same front data