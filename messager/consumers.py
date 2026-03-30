import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Hna t-sajal f-el DB w t-ba3th lel group
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': data['message']
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({'message': event['message']}))