from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from . import match
import time
import threading
from .models import Queue 
count = 0
t_count = 0 # tournament count
match_name = None
values = {}
queue = []
matches = {}
matchPlayers = {}
simpleMatchName = None
simpleMatchPlayers = [] # max 2 players
simpleMatchPlayersLogins = [] # max 2 players logins

tournaments = {}

class GameConsumer(WebsocketConsumer):
    def connect(self):
        global simpleMatchName, count
        #chamar tipo de matchjmaking especifico
        userId = Queue.objects.last().user_id
        login = Queue.objects.last().login
        matchType = Queue.objects.last().match_type
        gamemode = Queue.objects.last().gamemode
        self.accept()
        if matchType == '1v1':
            player = self.simpleMatch(login)
        elif matchType == 'tournament':
            player = self.tournamentfMatch(login)
        # elif matchType == 'tournament':
        #     player = self.tournamentMatch()
        else:
            self.close()
        print("CONNECTED, CHANNEL:", self.channel_name, simpleMatchName, player, count)

    def tournamentMatch(self, login):
        global t_count, match_name
        if t_count % 4 == 0:
            match_name = "tournament" + str(t_count // 2)
            player = 'a'

        #t_count = t_count + 1


    def doMatch(self):
        global count, simpleMatchPlayers, values, simpleMatchPlayersLogins

        match_name = "match" + str(count // 2)
        async_to_sync(self.channel_layer.group_add)(
            match_name, simpleMatchPlayers[0]
        )
        async_to_sync(self.channel_layer.group_add)(
            match_name, simpleMatchPlayers[1]
        )

        values[match_name] = {"aY": 270, "bY": 270}
        print("values: ", values)
        matches[match_name] = []
        matchPlayers[match_name] = []
        print("simpleMatchPlayers: ", simpleMatchPlayers)
        for player in simpleMatchPlayers:
            matches[match_name].append(player)
        print("matches: ", matches)
        for login in simpleMatchPlayersLogins:
            matchPlayers[match_name].append(login)
        print("matchPlayers: ", matchPlayers)
        return match_name

    def simpleMatch(self, login):
        global count, simpleMatchPlayers, simpleMatchPlayersLogins

        simpleMatchPlayers.append(self.channel_name)
        simpleMatchPlayersLogins.append(login)
        if count % 2 == 1:
            self.newMatch()
        if count % 2 == 0:
            count += 1
            return 'a'
        else:
            count += 1
            return 'b'

    def newMatch(self):
        global simpleMatchName

        simpleMatchName = self.doMatch()

        thread = threading.Thread(target=self.gameLoop, args=(simpleMatchName,))
        thread.daemon = True  # This allows the thread to exit when the main program exits
        thread.start()
        for player in simpleMatchPlayers:
            async_to_sync(self.channel_layer.send)(player, {"type":"handshake", "player": player, "match": simpleMatchName})
        simpleMatchPlayers.clear()
        print("STARTED GAME THREAD", simpleMatchName, matches[simpleMatchName])

    def receive(self, text_data):
        data = json.loads(text_data)
        #print("receive: ", data)
        if "aY" in data:
            values[data["match"]]["aY"] = data["aY"]
        elif "bY" in data:
            values[data["match"]]["bY"] = data["bY"]
        return

    def disconnect(self, close_code):
        global count
        if(self.channel_name in queue):
            count -= 1
            queue.clear()
        # find match based on channel name
        for match in matches:
            if(self.channel_name in matches[match]):
                matches[match].remove(self.channel_name)

        print("disconnect", close_code)
        pass

    def gameLoop(self, match_name):
        async_to_sync(self.channel_layer.group_send)(match_name,
            {
                "type":"send_game_data",
                "countDown": True 
            })
        # match.setupGameLoop(match_name, 'default')
        match.setupGameLoop(match_name, 'crazyPaddleSizes')
        time.sleep(4)
        while True:
            game_data = match.gameloop(match_name, {'aY': values[match_name]['aY'], 'bY': values[match_name]['bY']})
            async_to_sync(self.channel_layer.group_send)(match_name,
                {
                    "type":"send_game_data",
                    "data": game_data
                })
            if(game_data.get('scoreA') > 3 or game_data.get('scoreB') > 3):
                return #kill the thread
            if(len(matches[match_name]) < 2):
                async_to_sync(self.channel_layer.group_send)(match_name,
                    {
                        "type":"send_game_data",
                        "close": True
                    })
                return
            if(game_data.get('sound') == 'score'):
                time.sleep(1)
            time.sleep(11/1000)  # 10ms
            # print(f"match_name: {match_name} time: {(end-start) * 1000}")

    def send_game_data(self, event):
        global emits
        if("countDown" in event):
            self.send(text_data=json.dumps({
                "type":"countDown",
            }))
            return
        
        if("close" in event):
            self.send(text_data=json.dumps({
                "type":"close",
            }))
            return
        
        game_data = event["data"]
        self.send(text_data=json.dumps({
            "type":"gameState",
            "data": game_data
        }))
        emits+=1
        calcTime(match_name)


recv = 0
timeA = int(time.time() * 1000)
emits = 0

async def calcTime(match_name):
    global recv, timeA, emits
    recv = recv + 1
    timeB = int(time.time() * 1000)
    if (timeB - timeA >= 1000):
        print(f"match_name: {match_name} requests/s: {recv}, response/s:{emits}")
        timeA = timeB
        emits = 0
        recv = 0