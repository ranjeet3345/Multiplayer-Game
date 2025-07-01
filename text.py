# app/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LivePoolConsumer(AsyncWebsocketConsumer):
    # Format: {"group_name": {"username": {"is_ready": False, "channel_name": str}}}
    active_users = {}

    async def connect(self):
        self.pool_name = self.scope['url_route']['kwargs']['pool_name']
        self.group_name = f"livepool_{self.pool_name}"

        self.username = self.scope["user"].username if self.scope["user"].is_authenticated else self.channel_name

        if self.group_name not in LivePoolConsumer.active_users:
            LivePoolConsumer.active_users[self.group_name] = {}

        LivePoolConsumer.active_users[self.group_name][self.username] = {
            "is_ready": False,
            "channel_name": self.channel_name
        }

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        await self.broadcast_user_list()

    async def disconnect(self, close_code):
        group = LivePoolConsumer.active_users.get(self.group_name, {})
        if self.username in group:
            del group[self.username]

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        await self.broadcast_user_list()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("action") == "toggle_ready":
            current = LivePoolConsumer.active_users[self.group_name][self.username]
            current["is_ready"] = not current["is_ready"]
            await self.broadcast_user_list()

    async def broadcast_user_list(self):
        user_list = [
            {"username": name, "is_ready": details["is_ready"]}
            for name, details in LivePoolConsumer.active_users[self.group_name].items()
        ]
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_user_list",
                "users": user_list
            }
        )

    async def send_user_list(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_list",
            "users": event["users"]
        }))
