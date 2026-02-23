import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'chat_room'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope['user'].username if self.scope['user'].is_authenticated else '游客'

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user,
            }
        )

    # async def chat_message(self, event):
    #     await self.send(text_data=json.dumps({
    #         'message': event['message'],
    #         'user': event['user'],
    #         'timestamp': event['timestamp'],
    #     }))
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user'],
            'timestamp': event['timestamp'],
            'image': event.get('image', ''),
            'id': event['id'],
            'avatar': event.get('avatar', ''),
        }))

    async def chat_recall(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat.recall',
            'id': event['id'],
            'user': event['user'],  # ✅ 广播撤回者是谁
        }))
