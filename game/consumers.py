from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from . import match
import time
import threading
from .models import Queue

import time

count = 0
t_count = {}
match_name = None
values = {}

tournamentMatchName0 = None
tournamentMatchName1 = None
#tournamentMatchPlayers = [] # max 4 players
#tournamentMatchPlayersLogins = [] # max 4 players logins
tournamentMatchPlayers = {}
tournamentMatchPlayersLogins = {}

simpleMatchNameDefaultGameModeName = None
simpleMatchPlayersDefaultGameMode = [] # max 2 players
simpleMatchPlayersLoginsDefaultGameMode = [] # max 2 players logins

simpleMatchNameCrazyGameModeName = None
simpleMatchPlayersCrazyGameMode = [] # max 2 players
simpleMatchPlayersLoginsCrazyGameMode = [] # max 2 players logins

class GameConsumer(WebsocketConsumer):
    def connect(self):
        global simpleMatchName, count
        userId = Queue.objects.last().user_id
        login = Queue.objects.last().login
        matchType = Queue.objects.last().match_type
        gamemode = Queue.objects.last().gamemode
        matchSuggestedName = Queue.objects.last().match_suggested_name
        alias = Queue.objects.last().alias
        self.accept()
        if matchType == 'simpleMatch':
            player = self.simpleMatch(login, gamemode, alias)
        elif matchType == 'tournamentMatch':
            player = self.tournamentMatch(login, matchSuggestedName, alias)
        elif matchType == 'tournamentMatchFinal':
            player = self.simpleMatch(login, "defaultGameMode", alias) 
        else:
            self.close()


    def tournamentMatch(self, login, matchSuggestedName, alias):
        """
            Tournament match will have 4 players
            Two players will fight in a 1v1 match
            And another two players will fight in another 1v1 match
            The winners of each match will fight in a 1v1 match
            The winner of the last match will be the tournament winner
        """
        global t_count, tournamentMatchPlayers, tournamentMatchPlayersLogins

        if matchSuggestedName == '' or matchSuggestedName == None:
            matchSuggestedName = 'default'
        if not matchSuggestedName in tournamentMatchPlayers:
            tournamentMatchPlayers[matchSuggestedName] = []
            tournamentMatchPlayersLogins[matchSuggestedName] = []
        if not matchSuggestedName in t_count:
            t_count[matchSuggestedName] = 0
        tournamentMatchPlayers[matchSuggestedName].append(self.channel_name)
        if alias != '':
            tournamentMatchPlayersLogins[matchSuggestedName].append(alias)
        else:
            tournamentMatchPlayersLogins[matchSuggestedName].append(login)

        if t_count[matchSuggestedName] % 4 == 0:
            t_count[matchSuggestedName] += 1
            return 'a'
        elif t_count[matchSuggestedName] % 4 == 1:
            t_count[matchSuggestedName] += 1
            return 'b'
        elif t_count[matchSuggestedName] % 4 == 2:
            t_count[matchSuggestedName] += 1
            return 'a'
        elif t_count[matchSuggestedName] % 4 == 3:
            t_count[matchSuggestedName] += 1
            self.newTournamentMatch(matchSuggestedName)
            return 'b'


    def simpleMatch(self, login, gamemode, alias):
        global count, simpleMatchPlayersDefaultGameMode, simpleMatchPlayersLoginsDefaultGameMode, simpleMatchPlayersCrazyGameMode, simpleMatchPlayersLoginsCrazyGameMode

        if gamemode == 'defaultGameMode' or gamemode != 'crazyGameMode':
            simpleMatchPlayersDefaultGameMode.append(self.channel_name)
            if alias != '':
                simpleMatchPlayersLoginsDefaultGameMode.append(alias)
            else:
                simpleMatchPlayersLoginsDefaultGameMode.append(login)
        elif gamemode == 'crazyGameMode':
            simpleMatchPlayersCrazyGameMode.append(self.channel_name)
            if alias != '':
                simpleMatchPlayersLoginsCrazyGameMode.append(alias)
            else:
                simpleMatchPlayersLoginsCrazyGameMode.append(login)
        if count % 2 == 0:
            count += 1
            return 'a'
        else:
            count += 1
            self.newMatch(gamemode)
            return 'b'


    def doMatch(self, gamemode):
        global count, values, simpleMatchPlayersDefaultGameMode, simpleMatchPlayersLoginsDefaultGameMode, simpleMatchPlayersCrazyGameMode, simpleMatchPlayersLoginsCrazyGameMode

        if gamemode == 'defaultGameMode' or gamemode != 'crazyGameMode':
            match_name = "matchdefault" + str(count // 2)
            async_to_sync(self.channel_layer.group_add)(
                match_name, simpleMatchPlayersDefaultGameMode[0]
            )
            async_to_sync(self.channel_layer.group_add)(
                match_name, simpleMatchPlayersDefaultGameMode[1]
            )

            values[match_name] = {"aY": 270, "bY": 270}
            return match_name
        elif gamemode == 'crazyGameMode':
            match_name = "matchcrazy" + str(count // 2)
            async_to_sync(self.channel_layer.group_add)(
                match_name, simpleMatchPlayersCrazyGameMode[0]
            )
            async_to_sync(self.channel_layer.group_add)(
                match_name, simpleMatchPlayersCrazyGameMode[1]
            )

            values[match_name] = {"aY": 270, "bY": 270}
            return match_name


    def doTournamentMatch(self, matchSuggestedName):
        global t_count, tournamentMatchPlayers, values, tournamentMatchPlayersLogins

        tournament_match_name0 = "tournament" + str(t_count[matchSuggestedName] // 4) + "_0" + matchSuggestedName
        async_to_sync(self.channel_layer.group_add)(
            tournament_match_name0, tournamentMatchPlayers[matchSuggestedName][0]
        )
        async_to_sync(self.channel_layer.group_add)(
            tournament_match_name0, tournamentMatchPlayers[matchSuggestedName][1]
        )
        tournament_match_name1 = "tournament" + str(t_count[matchSuggestedName] // 4) + "_1" + matchSuggestedName
        async_to_sync(self.channel_layer.group_add)(
            tournament_match_name1, tournamentMatchPlayers[matchSuggestedName][2]
        )
        async_to_sync(self.channel_layer.group_add)(
            tournament_match_name1, tournamentMatchPlayers[matchSuggestedName][3]
        )

        values[tournament_match_name0] = {"aY": 270, "bY": 270}
        values[tournament_match_name1] = {"aY": 270, "bY": 270}
        return tournament_match_name0, tournament_match_name1
        

    def newMatch(self, gamemode):
        global simpleMatchNameDefaultGameModeName, simpleMatchNameCrazyGameModeName

        if gamemode == 'defaultGameMode' or gamemode != 'crazyGameMode':
            simpleMatchNameDefaultGameModeName = self.doMatch(gamemode)

            for i, simple_match_player in enumerate(simpleMatchPlayersDefaultGameMode):
                if (i == 0):
                    player = 'a'
                else:
                    player = 'b'
                async_to_sync(self.channel_layer.send)(simple_match_player, {"type":"handshake", "player": player, "match": simpleMatchNameDefaultGameModeName, "alias": {'a': simpleMatchPlayersLoginsDefaultGameMode[0], 'b': simpleMatchPlayersLoginsDefaultGameMode[1]}})
            time.sleep(1)
            thread = threading.Thread(target=self.gameLoop, args=(simpleMatchNameDefaultGameModeName,))
            thread.daemon = True  # This allows the thread to exit when the main program exits
            thread.start()
            simpleMatchPlayersDefaultGameMode.clear()
            simpleMatchPlayersLoginsDefaultGameMode.clear()
        elif gamemode == 'crazyGameMode':
            simpleMatchNameCrazyGameModeName = self.doMatch(gamemode)

            for i, simple_match_player in enumerate(simpleMatchPlayersCrazyGameMode):
                if (i == 0):
                    player = 'a'
                else:
                    player = 'b'
                async_to_sync(self.channel_layer.send)(simple_match_player, {"type":"handshake", "player": player, "match": simpleMatchNameCrazyGameModeName, "alias": {'a': simpleMatchPlayersLoginsCrazyGameMode[0], 'b': simpleMatchPlayersLoginsCrazyGameMode[1]}})
            time.sleep(1)
            thread = threading.Thread(target=self.gameLoop, args=(simpleMatchNameCrazyGameModeName,))
            thread.daemon = True  # This allows the thread to exit when the main program exits
            thread.start()
            simpleMatchPlayersCrazyGameMode.clear()
            simpleMatchPlayersLoginsCrazyGameMode.clear()


    def newTournamentMatch(self, matchSuggestedName):
        global tournamentMatchName0, tournamentMatchName1

        tournamentMatchName0, tournamentMatchName1 = self.doTournamentMatch(matchSuggestedName)

        for i, tournament_match_player in enumerate(tournamentMatchPlayers[matchSuggestedName]):
            if (i == 0):
                player = 'a'
                match_name = tournamentMatchName0
            elif (i == 1):
                player = 'b'
                match_name = tournamentMatchName0
            elif (i == 2):
                player = 'a'
                match_name = tournamentMatchName1
            elif (i == 3):
                player = 'b'
                match_name = tournamentMatchName1
            async_to_sync(self.channel_layer.send)(tournament_match_player, {"type":"handshake", "player": player, "match": match_name, "alias": {'a': tournamentMatchPlayersLogins[matchSuggestedName][0], 'b': tournamentMatchPlayersLogins[matchSuggestedName][1]}})
        time.sleep(1)
        thread = threading.Thread(target=self.gameLoop, args=(tournamentMatchName0,))
        thread.daemon = True
        thread.start()
        thread = threading.Thread(target=self.gameLoop, args=(tournamentMatchName1,))
        thread.daemon = True
        thread.start()
        tournamentMatchPlayers[matchSuggestedName].clear()
        tournamentMatchPlayersLogins[matchSuggestedName].clear()

    def receive(self, text_data):
        data = json.loads(text_data)
        if "aY" in data:
            values[data["match"]]["aY"] = data["aY"]
        elif "bY" in data:
            values[data["match"]]["bY"] = data["bY"]
        return

    def disconnect(self, close_code):
        global count, simpleMatchPlayersDefaultGameMode, simpleMatchPlayersLoginsDefaultGameMode, simpleMatchPlayersCrazyGameMode, simpleMatchPlayersLoginsCrazyGameMode, tournamentMatchPlayers, tournamentMatchPlayersLogins
        for player in simpleMatchPlayersDefaultGameMode:
            if (self.channel_name == player):
                index = simpleMatchPlayersDefaultGameMode.index(player)
                simpleMatchPlayersDefaultGameMode.pop(index)
                simpleMatchPlayersLoginsDefaultGameMode.pop(index)
                count -= 1
                break
        for player in simpleMatchPlayersCrazyGameMode:
            if (self.channel_name == player):
                index = simpleMatchPlayersCrazyGameMode.index(player)
                simpleMatchPlayersCrazyGameMode.pop(index)
                simpleMatchPlayersLoginsCrazyGameMode.pop(index)
                count -= 1
                break
        for matchSuggestedName in tournamentMatchPlayers:
            for player in tournamentMatchPlayers[matchSuggestedName]:
                if (self.channel_name == player):
                    index = tournamentMatchPlayers[matchSuggestedName].index(player)
                    tournamentMatchPlayers[matchSuggestedName].pop(index)
                    tournamentMatchPlayersLogins[matchSuggestedName].pop(index)
                    t_count[matchSuggestedName] -= 1
                    break


    def gameLoop(self, match_name):
        async_to_sync(self.channel_layer.group_send)(match_name,
            {
                "type":"send_game_data",
                "countDown": True 
            })
        gamemode = 'defaultGameMode'
        if match_name.startswith("matchdefault"):
            match.setupGameLoop(match_name, gamemode)
        elif match_name.startswith("matchcrazy"):
            gamemode = 'crazyGameMode'
            match.setupGameLoop(match_name, gamemode)
        elif match_name.startswith("tournament"):
            match.setupGameLoop(match_name, gamemode)
        time.sleep(4)
        while True:
            game_data = match.gameloop(match_name, gamemode, {'aY': values[match_name]['aY'], 'bY': values[match_name]['bY']})
            async_to_sync(self.channel_layer.group_send)(match_name,
                {
                    "type":"send_game_data",
                    "data": game_data
                })
            if(game_data.get('scoreA') > 3 or game_data.get('scoreB') > 3):
                winner = None
                if (game_data.get('scoreA') > game_data.get('scoreB')):
                    winner = 'a'
                elif (game_data.get('scoreA') < game_data.get('scoreB')):
                    winner = 'b'
                async_to_sync(self.channel_layer.group_send)(match_name,
                        {
                            "type":"send_game_data",
                            "winner": winner
                        })
                return #kill the thread
            if(game_data.get('sound') == 'score'):
                time.sleep(1)
            time.sleep(11/1000)  # 10ms

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

        if ("winner" in event):
            self.send(text_data=json.dumps({
                "type":"gameWinner",
                "winner": event["winner"]
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
        self.send(text_data=json.dumps({
            "type":"handshake",
            "player": event["player"],
            "match": event["match"],
            "alias": event["alias"]
        }))

recv = 0
timeA = int(time.time() * 1000)
emits = 0

async def calcTime(match_name):
    global recv, timeA, emits
    recv = recv + 1
    timeB = int(time.time() * 1000)
    if (timeB - timeA >= 1000):
        timeA = timeB
        emits = 0
        recv = 0