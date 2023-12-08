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
        self.accept()
        print("DEFINING MATCH TYPE")
        if matchType == 'simpleMatch':
            player = self.simpleMatch(login, gamemode)
        elif matchType == 'tournamentMatch':
            player = self.tournamentMatch(login, matchSuggestedName)
        elif matchType == 'tournamentMatchFinal':
            player = self.simpleMatch(login, "defaultGameMode") 
        else:
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

        if matchSuggestedName == '' or matchSuggestedName == None:
            matchSuggestedName = 'default'
        if not matchSuggestedName in tournamentMatchPlayers:
            tournamentMatchPlayers[matchSuggestedName] = []
            tournamentMatchPlayersLogins[matchSuggestedName] = []
        if not matchSuggestedName in t_count:
            t_count[matchSuggestedName] = 0
        tournamentMatchPlayers[matchSuggestedName].append(self.channel_name)
        print("TOURNAMENT MATCH PLAYERS: ", tournamentMatchPlayers)
        tournamentMatchPlayersLogins[matchSuggestedName].append(login)
        print("TOURNAMENT MATCH PLAYERS LOGINS: ", tournamentMatchPlayersLogins)

        if t_count[matchSuggestedName] % 4 == 0:
            t_count[matchSuggestedName] += 1
            print("PLAYER A")
            return 'a'
        elif t_count[matchSuggestedName] % 4 == 1:
            t_count[matchSuggestedName] += 1
            print("PLAYER B")
            return 'b'
        elif t_count[matchSuggestedName] % 4 == 2:
            t_count[matchSuggestedName] += 1
            print("PLAYER C")
            return 'a'
        elif t_count[matchSuggestedName] % 4 == 3:
            t_count[matchSuggestedName] += 1
            print("PLAYER D")
            self.newTournamentMatch(matchSuggestedName)
            return 'b'


    def simpleMatch(self, login, gamemode):
        global count, simpleMatchPlayersDefaultGameMode, simpleMatchPlayersLoginsDefaultGameMode, simpleMatchPlayersCrazyGameMode, simpleMatchPlayersLoginsCrazyGameMode

        if gamemode == 'defaultGameMode' or gamemode != 'crazyGameMode':
            simpleMatchPlayersDefaultGameMode.append(self.channel_name)
            print("SIMPLE MATCH PLAYERS DEFAULT GAME MODE: ", simpleMatchPlayersDefaultGameMode)
            simpleMatchPlayersLoginsDefaultGameMode.append(login)
            print("SIMPLE MATCH PLAYERS LOGINS DEFAULT GAME MODE: ", simpleMatchPlayersLoginsDefaultGameMode)
        elif gamemode == 'crazyGameMode':
            simpleMatchPlayersCrazyGameMode.append(self.channel_name)
            print("SIMPLE MATCH PLAYERS CRAZY GAME MODE: ", simpleMatchPlayersCrazyGameMode)
            simpleMatchPlayersLoginsCrazyGameMode.append(login)
            print("SIMPLE MATCH PLAYERS LOGINS CRAZY GAME MODE: ", simpleMatchPlayersLoginsCrazyGameMode)
        if count % 2 == 0:
            count += 1
            print("PLAYER A")
            return 'a'
        else:
            count += 1
            print("PLAYER B")
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
            print("VALUES: ", values)
            print("SIMPLE MATCH PLAYERS: ", simpleMatchPlayersDefaultGameMode)
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
            print("VALUES: ", values)
            print("SIMPLE MATCH PLAYERS: ", simpleMatchPlayersCrazyGameMode)
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
        print("VALUES: ", values)
        print("TOURNAMENT MATCH PLAYERS: ", tournamentMatchPlayers)
        return tournament_match_name0, tournament_match_name1
        

    def newMatch(self, gamemode):
        global simpleMatchNameDefaultGameModeName, simpleMatchNameCrazyGameModeName

        if gamemode == 'defaultGameMode' or gamemode != 'crazyGameMode':
            print("BEFORE NEW MATCH", simpleMatchPlayersDefaultGameMode)
            simpleMatchNameDefaultGameModeName = self.doMatch(gamemode)
            print("AFTER NEW MATCH: ", simpleMatchNameDefaultGameModeName)

            print("SEND MESSAGE TO EACH PLAYER")
            for i, simple_match_player in enumerate(simpleMatchPlayersDefaultGameMode):
                if (i == 0):
                    player = 'a'
                else:
                    player = 'b'
                print("SEND MESSAGE TO: SIMPLE MATCH PLAYER: ", simple_match_player, "PLAYER:", player)
                async_to_sync(self.channel_layer.send)(simple_match_player, {"type":"handshake", "player": player, "match": simpleMatchNameDefaultGameModeName})
            print("START GAME THREAD")
            time.sleep(1)
            thread = threading.Thread(target=self.gameLoop, args=(simpleMatchNameDefaultGameModeName,))
            thread.daemon = True  # This allows the thread to exit when the main program exits
            thread.start()
            print("CLEAR SIMPLE MATCH PLAYERS")
            simpleMatchPlayersDefaultGameMode.clear()
            simpleMatchPlayersLoginsDefaultGameMode.clear()
            print("STARTED GAME THREAD", simpleMatchNameDefaultGameModeName)
        elif gamemode == 'crazyGameMode':
            print("BEFORE NEW MATCH", simpleMatchPlayersCrazyGameMode)
            simpleMatchNameCrazyGameModeName = self.doMatch(gamemode)
            print("AFTER NEW MATCH: ", simpleMatchNameCrazyGameModeName)

            print("SEND MESSAGE TO EACH PLAYER")
            for i, simple_match_player in enumerate(simpleMatchPlayersCrazyGameMode):
                if (i == 0):
                    player = 'a'
                else:
                    player = 'b'
                print("SEND MESSAGE TO: SIMPLE MATCH PLAYER: ", simple_match_player, "PLAYER:", player)
                async_to_sync(self.channel_layer.send)(simple_match_player, {"type":"handshake", "player": player, "match": simpleMatchNameCrazyGameModeName})
            print("START GAME THREAD")
            time.sleep(1)
            thread = threading.Thread(target=self.gameLoop, args=(simpleMatchNameCrazyGameModeName,))
            thread.daemon = True  # This allows the thread to exit when the main program exits
            thread.start()
            print("CLEAR SIMPLE MATCH PLAYERS")
            simpleMatchPlayersCrazyGameMode.clear()
            simpleMatchPlayersLoginsCrazyGameMode.clear()
            print("STARTED GAME THREAD", simpleMatchNameCrazyGameModeName)


    def newTournamentMatch(self, matchSuggestedName):
        global tournamentMatchName0, tournamentMatchName1

        print("BEFORE NEW TOURNAMENT MATCH", tournamentMatchPlayers)
        tournamentMatchName0, tournamentMatchName1 = self.doTournamentMatch(matchSuggestedName)
        print("AFTER NEW TOURNAMENT MATCH: ", "0:", tournamentMatchName0, "1:", tournamentMatchName1)

        print("SEND MESSAGE TO EACH PLAYER")
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
        tournamentMatchPlayers[matchSuggestedName].clear()
        tournamentMatchPlayersLogins[matchSuggestedName].clear()
        print("STARTED GAME THREAD. MATCH NAME 0:", tournamentMatchName0, "MATCH NAME 1:", tournamentMatchName1)

    def receive(self, text_data):
        data = json.loads(text_data)
        #print("RECEIVE: ", data)
        if "aY" in data:
            values[data["match"]]["aY"] = data["aY"]
        elif "bY" in data:
            values[data["match"]]["bY"] = data["bY"]
        return

    def disconnect(self, close_code):
        global count, simpleMatchPlayersDefaultGameMode, simpleMatchPlayersLoginsDefaultGameMode, simpleMatchPlayersCrazyGameMode, simpleMatchPlayersLoginsCrazyGameMode, tournamentMatchPlayers, tournamentMatchPlayersLogins
        print("DISCONNECTING", self.channel_name)
        for player in simpleMatchPlayersDefaultGameMode:
            if (self.channel_name == player):
                index = simpleMatchPlayersDefaultGameMode.index(player)
                print("INDEX: ", index)
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
        print("DISCONNECT", "CLOSE CODE:", close_code, "CHANNEL NAME:", self.channel_name)


    def gameLoop(self, match_name):
        print("GAME LOOP JUST STARTED")
        async_to_sync(self.channel_layer.group_send)(match_name,
            {
                "type":"send_game_data",
                "countDown": True 
            })
        print("GAME LOOP MATCH NAME: ", match_name)
        gamemode = 'defaultGameMode'
        if match_name.startswith("matchdefault"):
            match.setupGameLoop(match_name, gamemode)
        elif match_name.startswith("matchcrazy"):
            gamemode = 'crazyGameMode'
            match.setupGameLoop(match_name, gamemode)
        elif match_name.startswith("tournament"):
            match.setupGameLoop(match_name, gamemode)
        print("STARTING gameLoop MATCH NAME: ", match_name)
        time.sleep(4)
        while True:
            game_data = match.gameloop(match_name, gamemode, {'aY': values[match_name]['aY'], 'bY': values[match_name]['bY']})
            async_to_sync(self.channel_layer.group_send)(match_name,
                {
                    "type":"send_game_data",
                    "data": game_data
                })
            if(game_data.get('scoreA') > 0 or game_data.get('scoreB') > 0):
                print("GAME OVER")
                winner = None
                if (game_data.get('scoreA') > game_data.get('scoreB')):
                    winner = 'a'
                elif (game_data.get('scoreA') < game_data.get('scoreB')):
                    winner = 'b'
                print("WINNER: ", winner)
                async_to_sync(self.channel_layer.group_send)(match_name,
                        {
                            "type":"send_game_data",
                            "winner": winner
                        })
                return #kill the thread
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
        print("HANDSHAKE")
        print("EVENT PLAYER: ", event['player'])
        print("EVENT MATCH: ", event['match'])
        self.send(text_data=json.dumps({
            "type":"handshake",
            "player": event["player"],
            "match": event["match"],
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