from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from . import match
import time
import threading
from .models import Queue

import time

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
tournamentMatchName0 = None
tournamentMatchName1 = None
tournamentMatchPlayers = [] # max 4 players
tournamentMatchPlayersLogins = [] # max 4 players logins


tournaments = {}

class GameConsumer(WebsocketConsumer):
    def connect(self):
        print("-------------------------")
        global simpleMatchName, count
        userId = Queue.objects.last().user_id
        login = Queue.objects.last().login
        matchType = Queue.objects.last().match_type
        gamemode = Queue.objects.last().gamemode
        matchSuggestedName = Queue.objects.last().match_suggested_name
        print("MATCH TYPE: ", matchType)
        print("GAMEMODE: ", gamemode)
        self.accept()
        print("DEFINING MATCH TYPE")
        if matchType == 'simpleMatch':
            print("CONNECTION ACCEPETED, 1v1 MATCH")
            player = self.simpleMatch(login)
            print("PLAYER: ", player)
            print("CONNECTED, CHANNEL:", self.channel_name, "MATCH NAME:", simpleMatchName, "PLAYER:", player, "COUNT:", count)
        elif matchType == 'tournamentMatch':
            print("CONNECTION ACCEPETED, TOURNAMENT MATCH")
            player = self.tournamentMatch(login, matchSuggestedName) 
            print("PLAYER: ", player)
            print("CONNECTED, CHANNEL:", self.channel_name, "MATCH NAME 0:", tournamentMatchName0, "MATCH NAME 1:", tournamentMatchName1, "PLAYER:", player, "T_COUNT:", t_count)
        elif matchType == 'tournamentMatchFinal':
            print("CONNECTION ACCEPETED, TOURNAMENT MATCH FINAL")
            player = self.simpleMatch(login) 
            print("PLAYER: ", player)
            print("CONNECTED, CHANNEL:", self.channel_name, "MATCH NAME:", simpleMatchName, "PLAYER:", player, "COUNT:", count)
        else:
            print("MATCH TYPE NOT FOUND, SO CONNECTION CLOSE")
            self.close()


    def tournamentMatch(self, login, matchSuggestedName):
        """
            Tournament match will have 4 players
            Two players will fight in a 1v1 match
            And another two players will fight in another 1v1 match
            The winners of each match will fight in a 1v1 match
            The winner of the last match will be the tournament winner
        """
        global t_count, tournaments, tournamentMatchPlayers, tournamentMatchPlayersLogins

        tournamentMatchPlayers.append(self.channel_name)
        print("TOURNAMENT MATCH PLAYERS: ", tournamentMatchPlayers)
        tournamentMatchPlayersLogins.append(login)
        print("TOURNAMENT MATCH PLAYERS LOGINS: ", tournamentMatchPlayersLogins)

        if t_count % 4 == 0:
            t_count += 1
            print("PLAYER A")
            return 'a'
        elif t_count % 4 == 1:
            t_count += 1
            print("PLAYER B")
            return 'b'
        elif t_count % 4 == 2:
            t_count += 1
            print("PLAYER C")
            return 'a'
        elif t_count % 4 == 3:
            t_count += 1
            print("PLAYER D")
            self.newTournamentMatch(matchSuggestedName)
            return 'b'


    def simpleMatch(self, login):
        global count, simpleMatchPlayers, simpleMatchPlayersLogins

        simpleMatchPlayers.append(self.channel_name)
        print("SIMPLE MATCH PLAYERS: ", simpleMatchPlayers)
        simpleMatchPlayersLogins.append(login)
        print("SIMPLE MATCH PLAYERS LOGINS: ", simpleMatchPlayersLogins)  
        if count % 2 == 0:
            count += 1
            print("PLAYER A")
            return 'a'
        else:
            count += 1
            print("PLAYER B")
            self.newMatch()
            return 'b'


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
        print("VALUES: ", values)
        matches[match_name] = []
        matchPlayers[match_name] = []
        print("SIMPLE MATCH PLAYERS: ", simpleMatchPlayers)
        for player in simpleMatchPlayers:
            matches[match_name].append(player)
        print("MATCHES: ", matches)
        for login in simpleMatchPlayersLogins:
            matchPlayers[match_name].append(login)
        print("MATCH PLAYERS: ", matchPlayers)
        return match_name


    def doTournamentMatch(self, matchSuggestedName):
        global t_count, tournamentMatchPlayers, values, tournamentMatchPlayersLogins

        tournament_match_name0 = "tournament" + str(t_count // 4) + "_0" + matchSuggestedName
        async_to_sync(self.channel_layer.group_add)(
            tournament_match_name0, tournamentMatchPlayers[0]
        )
        async_to_sync(self.channel_layer.group_add)(
            tournament_match_name0, tournamentMatchPlayers[1]
        )
        tournament_match_name1 = "tournament" + str(t_count // 4) + "_1" + matchSuggestedName
        async_to_sync(self.channel_layer.group_add)(
            tournament_match_name1, tournamentMatchPlayers[2]
        )
        async_to_sync(self.channel_layer.group_add)(
            tournament_match_name1, tournamentMatchPlayers[3]
        )

        values[tournament_match_name0] = {"aY": 270, "bY": 270}
        values[tournament_match_name1] = {"aY": 270, "bY": 270}
        print("VALUES: ", values)
        matches[tournament_match_name0] = []
        matches[tournament_match_name1] = []
        matchPlayers[tournament_match_name0] = []
        matchPlayers[tournament_match_name1] = []
        print("TOURNAMENT MATCH PLAYERS: ", tournamentMatchPlayers)
        matches[tournament_match_name0].append(tournamentMatchPlayers[0])
        matches[tournament_match_name0].append(tournamentMatchPlayers[1])
        matches[tournament_match_name1].append(tournamentMatchPlayers[2])
        matches[tournament_match_name1].append(tournamentMatchPlayers[3])
        print("MATCHES: ", matches)
        matchPlayers[tournament_match_name0].append(tournamentMatchPlayersLogins[0])
        matchPlayers[tournament_match_name0].append(tournamentMatchPlayersLogins[1])
        matchPlayers[tournament_match_name1].append(tournamentMatchPlayersLogins[2])
        matchPlayers[tournament_match_name1].append(tournamentMatchPlayersLogins[3])
        print("MATCH PLAYERS: ", matchPlayers)
        return tournament_match_name0, tournament_match_name1
        

    def newMatch(self):
        global simpleMatchName

        print("BEFORE NEW MATCH", simpleMatchPlayers)
        simpleMatchName = self.doMatch()
        print("AFTER NEW MATCH: ", simpleMatchName)

        print("SEND MESSAGE TO EACH PLAYER")
        for i, simple_match_player in enumerate(simpleMatchPlayers):
            if (i == 0):
                player = 'a'
            else:
                player = 'b'
            print("SEND MESSAGE TO: SIMPLE MATCH PLAYER: ", simple_match_player, "PLAYER:", player)
            async_to_sync(self.channel_layer.send)(simple_match_player, {"type":"handshake", "player": player, "match": simpleMatchName})
        print("START GAME THREAD")
        time.sleep(1)
        thread = threading.Thread(target=self.gameLoop, args=(simpleMatchName,))
        thread.daemon = True  # This allows the thread to exit when the main program exits
        thread.start()
        print("CLEAR SIMPLE MATCH PLAYERS")
        simpleMatchPlayers.clear()
        simpleMatchPlayersLogins.clear()
        print("STARTED GAME THREAD", simpleMatchName, matches[simpleMatchName])


    def newTournamentMatch(self, matchSuggestedName):
        global tournamentMatchName0, tournamentMatchName1

        print("BEFORE NEW TOURNAMENT MATCH", tournamentMatchPlayers)
        tournamentMatchName0, tournamentMatchName1 = self.doTournamentMatch(matchSuggestedName)
        print("AFTER NEW TOURNAMENT MATCH: ", "0:", tournamentMatchName0, "1:", tournamentMatchName1)

        print("SEND MESSAGE TO EACH PLAYER")
        for i, tournament_match_player in enumerate(tournamentMatchPlayers):
            if (i == 0):
                player = 'a'
                match_name = tournamentMatchName0
            elif (i == 1):
                player = 'b'
                match_name = tournamentMatchName0
            elif (i == 2):
                player = 'a'
                match_name = tournamentMatchName1
            else:
                player = 'b'
                match_name = tournamentMatchName1
            print("SEND MESSAGE TO: TOURNAMENT MATCH PLAYER: ", tournament_match_player, "PLAYER:", player, "MATCH:", match_name)
            async_to_sync(self.channel_layer.send)(tournament_match_player, {"type":"handshake", "player": player, "match": match_name})
        print("START GAME THREAD")
        time.sleep(1)
        thread = threading.Thread(target=self.gameLoop, args=(tournamentMatchName0,))
        thread.daemon = True
        thread.start()
        thread = threading.Thread(target=self.gameLoop, args=(tournamentMatchName1,))
        thread.daemon = True
        thread.start()
        print("CLEAR TOURNAMENT MATCH PLAYERS")
        tournamentMatchPlayers.clear()
        tournamentMatchPlayersLogins.clear()
        print("STARTED GAME THREAD. MATCH NAME 0:", tournamentMatchName0, matches[tournamentMatchName0], "MATCH NAME 1:", tournamentMatchName1, matches[tournamentMatchName1])

    def receive(self, text_data):
        data = json.loads(text_data)
        #print("RECEIVE: ", data)
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

        print("DISCONNECT", close_code)


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

    def handshake(self, event):
        print("HANDSHAKE")
        print("EVENT PLAYER: ", event['player'])
        print("EVENT MATCH: ", event['match'])
        self.send(text_data=json.dumps({
            "type":"handshake",
            "player": event["player"],
            "match": event["match"]
        }))

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