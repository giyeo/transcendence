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
            values[match_name] = {"aY": 0, "bY": 0}
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
        self.send(text_data=json.dumps({"player": player, "match": match_name}))
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
        time.sleep(4)
        while True:
            #if values[match_name]["aY"] is not None and values[match_name]["bY"] is not None:
            game_data = server.gameloop(match_name, {'aY': values[match_name]['aY'], 'bY': values[match_name]['bY']})
            async_to_sync(self.channel_layer.group_send)(match_name,
                {
                    "type":"send_game_data",
                    "data": game_data
                }
            )
            if(game_data.get('sound') == 'score'):
                time.sleep(1)
            time.sleep(12 / 1000)  # 12ms

    def send_game_data(self, event):
        game_data = event["data"]
        self.send(text_data=json.dumps({
            "data": game_data
        }))
