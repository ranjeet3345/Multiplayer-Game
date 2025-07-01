from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

class MyConsumer(JsonWebsocketConsumer):
    def connect(self):
        print("websocket connected .....")

        print("channel layer->",self.channel_layer)
        print("channel name->",self.channel_name)
        self.group_name=self.scope['url_route']['kwargs']['groupkaname']

        print('group name->',self.group_name)

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def receive_json(self, content, **kwargs):
        print("msg received from client ->>>>",content)
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chat.message',
                'message' : content['msg']

            }
        )

    def disconnect(self, close_code):
        print(">>> Web socket DisCONNECTED ....",close_code)
        print("channel layer->",self.channel_layer)
        print("channel name->",self.channel_name)
        

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
    