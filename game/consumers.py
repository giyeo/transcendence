from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from . import server
import time
import asyncio
import threading

group_count = {}


count = 0
match_name = None
values = {}

class GameConsumer(WebsocketConsumer):
    def connect(self):
        new_match = False
        global match_name, count
        global valueA, valueB
        if count % 2 == 0:
            match_name = "match" + str(count)
            player = 'a'
            values[match_name] = {"aY": 270, "bY": 270}
        else:
            player = 'b'
            new_match = True
        print("CONNECTED, CHANNEL:", self.channel_name, match_name, player, count)
        # self.update_group_.count(match_name, 1)
        async_to_sync(self.channel_layer.group_add)(
            match_name, self.channel_name
        )
        #implement matchmaking here
        count += 1
        self.accept()
        self.send(text_data=json.dumps({"type":"handshake", "player": player, "match": match_name}))
        if new_match:
            self.newMatch(match_name)

    def newMatch(self, match_name):
        thread = threading.Thread(target=self.gameLoop, args=(match_name,))
        thread.daemon = True  # This allows the thread to exit when the main program exits
        thread.start()
        print("STARTED THREAD", match_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        match = None
        if "match" in data:
            match = data["match"]
        if "aY" in data:
            values[match]["aY"] = data["aY"]
        elif "bY" in data:
            values[match]["bY"] = data["bY"]
        return 

    def disconnect(self, close_code):
        print("disconnect")
        pass
    
    def gameLoop(self, match_name):
        async_to_sync(self.channel_layer.group_send)(match_name,
            {
                "type":"send_game_data",
                "countDown": True 
            })
        time.sleep(4)
        server.setupGameLoop()
        while True:
            #if values[match_name]["aY"] is not None and values[match_name]["bY"] is not None:
            game_data = server.gameloop(match_name, {'aY': values[match_name]['aY'], 'bY': values[match_name]['bY']})
            #time taken in ms
            async_to_sync(self.channel_layer.group_send)(match_name,
                {
                    "type":"send_game_data",
                    "data": game_data
                })
            if(game_data.get('scoreA') > 3 or game_data.get('scoreB') > 3):
                #disconnect all people inside the group
                # async_to_sync(self.channel_layer.group_send)(match_name,{"type":"close"})
                return #kill the thread
            if(game_data.get('sound') == 'score'):
                time.sleep(1)
            time.sleep(10/1000)  # 12ms
    
    def send_game_data(self, event):
        global emits
        if("countDown" in event):
            self.send(text_data=json.dumps({
                "type":"countDown",
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

def calcTime(match_name):
	global recv, timeA, emits
	recv = recv + 1
	timeB = int(time.time() * 1000)
	if (timeB - timeA >= 1000):
		print(f"match_name: {match_name} requests/s: {recv}, response/s:{emits}")
		timeA = timeB
		emits = 0
		recv = 0