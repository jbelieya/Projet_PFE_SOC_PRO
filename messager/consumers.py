import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def set_user_online(self, user_id, status):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            user.is_online = status
            user.save()
        except User.DoesNotExist:
            pass
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs'].get('user_id')

        if self.user_id:
            self.user_group_name = f'user_{self.user_id}'
            
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)
            
            await self.channel_layer.group_add("global_notifications", self.channel_name)

            await self.accept()
            await self.set_user_online(self.user_id, True)
            await self.channel_layer.group_send(
                "global_notifications",
                {
                    'type': 'status_update', 
                    'user_id': self.user_id,
                    'status': 'online'
                }
            )
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
            await self.channel_layer.group_discard("global_notifications", self.channel_name)
            await self.set_user_online(self.user_id, False)
            await self.channel_layer.group_send(
                "global_notifications",
                {
                    'type': 'status_update',
                    'user_id': self.user_id,
                    'status': 'offline'
                }
            )

    async def status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'user_id': event['user_id'],
            'status': event['status']
        }))
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        sent_date = timezone.now().isoformat()

        await self.save_message(sender_id, receiver_id, message)

        await self.channel_layer.group_send(
            f"user_{receiver_id}",
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'sent_date': sent_date
            }
        )

    
        await self.channel_layer.group_send(
            f"user_{sender_id}",
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'sent_date': sent_date,
                'is_confirmation': True 
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'receiver_id': event['receiver_id'],
            'sent_date': event['sent_date'],
            'type': 'incoming_message'
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message):
        from .models import ChatView
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            sender = User.objects.get(id=sender_id)
            receiver = User.objects.get(id=receiver_id)
            ChatView.objects.create(
                sender=sender,
                receiver=receiver,
                textContent=message,
                sent_date=timezone.now()
            )
        except Exception as e:
            print(f"Error saving message: {e}")