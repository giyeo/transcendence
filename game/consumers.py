from channels.generic.websocket import WebsocketConsumer
import json

from . import server

class GameConsumer(WebsocketConsumer):
    def connect(self):
        print("connect")
        self.accept()


    def receive(self, text_data):
        data = json.loads(text_data)
        if "aY" not in data and "bY" not in data:
            return
        game_data = server.gameloop(self.channel_name, {'aY': data["aY"], 'bY': data["bY"]})
        self.send(text_data=json.dumps({"data": game_data}))


    def disconnect(self, close_code):
        print("disconnect")
        pass
