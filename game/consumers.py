from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from . import server
import time

group_count = {}



class GameConsumer(WebsocketConsumer):
    def connect(self):
        print("CONNECTED, CHANNEL:", self.channel_name)
        self.room_group_name = "match"
        if len(group_count) % 2 == 0:
            player = 'a'
        else:
            player = 'b'
        self.update_group_count(self.room_group_name, 1)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        #implement matchmaking here
        time.sleep(1)
        self.accept()
        self.send(text_data=json.dumps({"player": player}))


    def receive(self, text_data):
        data = json.loads(text_data)
        if "aY" not in data and "bY" not in data:
            return
        game_data = server.gameloop(self.room_group_name, {'aY': data["aY"], 'bY': data["bY"]})
        # self.send(text_data=json.dumps({"data": game_data}))
        time.sleep(12/1000)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {"data": game_data}
        )

    def disconnect(self, close_code):
        print("disconnect")
        pass

    def update_group_count(self, group_name, count_change):
        if group_name in group_count:
            group_count[group_name] += count_change
        else:
            group_count[group_name] = count_change