from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from . import server
import time

group_count = {}


count = 0
room_group_name = None
values = {}

class GameConsumer(WebsocketConsumer):
    def connect(self):
        global room_group_name, count
        global valueA, valueB
        if count % 2 == 0:
            room_group_name = "match" + str(count)
            player = 'a'
            values[room_group_name] = {"aY": 0, "bY": 0}
        else:
            player = 'b'
        print("CONNECTED, CHANNEL:", self.channel_name, room_group_name, player, count)
        # self.update_group_.count(room_group_name, 1)
        async_to_sync(self.channel_layer.group_add)(
            room_group_name, self.channel_name
        )
        #implement matchmaking here
        count += 1
        self.accept()
        self.send(text_data=json.dumps({"player": player, "match": room_group_name}))

    def receive(self, text_data):
        data = json.loads(text_data)
        match = None
        if "match" in data:
            match = data["match"]
        if "aY" in data:
            values[match]["aY"] = data["aY"]
        elif "bY" in data:
            values[match]["bY"] = data["bY"]
        else:
            return
        if values[match]["aY"] == None and values[match]["bY"] == None:
            return

        if(data["player"] and data["player"] == 'a'):
            game_data = server.gameloop(match, {'aY': values[match]['aY'], 'bY': values[match]['bY']})
        else:
            return
        async_to_sync(self.channel_layer.group_send)(
            match,
            {
                "type":"send_game_data",
                "data": game_data
            }
        )
        # values[match]["aY"] = None
        # values[match]["bY"] = None

    def send_game_data(self, event):
        game_data = event["data"]
        self.send(text_data=json.dumps({
            "data": game_data
        }))

    def disconnect(self, close_code):
        print("disconnect")
        pass

    def update_group_count(self, group_name, count_change):
        if group_name in group_count:
            group_count[group_name] += count_change
        else:
            group_count[group_name] = count_change