from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid  # for auto room generation

class LivePoolConsumer(AsyncWebsocketConsumer):
    # Format: {"group_name": {"username": {"is_ready": False, "channel_name": str}}}
    active_users = {}

    async def connect(self):
        self.pool_name = self.scope['url_route']['kwargs']['pool_name']
        self.group_name = f"livepool_{self.pool_name}"

        print("poolname ->", self.pool_name)
        print("group_name ->", self.group_name)

        self.username = self.scope["user"].username if self.scope["user"].is_authenticated else self.channel_name
        print("username ->", self.username)

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

        elif data.get("action") == "send_invite":
            # Send invite to specific user
            target_user = data.get("target")
            if target_user in LivePoolConsumer.active_users[self.group_name]:
                target_channel = LivePoolConsumer.active_users[self.group_name][target_user]["channel_name"]
                await self.channel_layer.send(target_channel, {
                    "type": "receive_invite",
                    "from_user": self.username
                })

        elif data.get("action") == "invite_response":
            # Accept/reject response with room ID if accepted
            to_user = data.get("to_user")
            response = data.get("response")  # 'accepted' or 'rejected'

            if to_user in LivePoolConsumer.active_users[self.group_name]:
                to_channel = LivePoolConsumer.active_users[self.group_name][to_user]["channel_name"]

                response_payload = {
                    "type": "receive_invite_response",
                    "from_user": self.username,
                    "response": response
                }

                # If accepted, generate a room ID and include it
                if response == "accepted":
                    room_id = uuid.uuid4().hex[:8]
                    response_payload["room_id"] = room_id

                    # Notify responder also (current user)
                    await self.send(text_data=json.dumps({
                        "type": "invite_response",
                        "from": to_user,
                        "response": response,
                        "room_id": room_id
                    }))
                else:
                    # Notify responder also (current user)
                    await self.send(text_data=json.dumps({
                        "type": "invite_response",
                        "from": to_user,
                        "response": response
                    }))

                # Notify the initiator of the invite
                await self.channel_layer.send(to_channel, response_payload)

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

    async def receive_invite(self, event):
        await self.send(text_data=json.dumps({
            "type": "invite",
            "from": event["from_user"]
        }))

    async def receive_invite_response(self, event):
        # Send invite response with room_id if included
        response_data = {
            "type": "invite_response",
            "from": event["from_user"],
            "response": event["response"]
        }
        if "room_id" in event:
            response_data["room_id"] = event["room_id"]

        await self.send(text_data=json.dumps(response_data))




rooms = {}

class GameRoom(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'room_{self.room_name}'
        self.username = self.scope["user"].username if self.scope["user"].is_authenticated else self.channel_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Assign symbol
        if self.room_group_name not in rooms:
            rooms[self.room_group_name] = {
                "players": {}
            }

        players = rooms[self.room_group_name]["players"]
        symbol = "X" if "X" not in players.values() else "O"
        players[self.username] = symbol

        # Notify player of assignment
        await self.send(text_data=json.dumps({
            "type": "game_data",
            "payload": {
                "type": "assign",
                "symbol": symbol,
                "turn": symbol == "X"  # X starts first
            }
        }))

        # Optional: Broadcast join
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "player_join",
            "message": f"{self.username} joined as {symbol}"
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # Optionally remove from `rooms` tracking

    async def receive(self, text_data):
        data = json.loads(text_data)
        payload = data.get("data")
        payload["username"] = self.username

        await self.channel_layer.group_send(self.room_group_name, {
            "type": "run_game",
            "payload": json.dumps(payload),
            "sender": self.username
        })

    async def run_game(self, event):
        await self.send(text_data=json.dumps({
            "type": "game_data",
            "payload": json.loads(event["payload"])
        }))

    async def player_join(self, event):
        await self.send(text_data=json.dumps({
            "type": "player_join",
            "message": event["message"]
        }))
