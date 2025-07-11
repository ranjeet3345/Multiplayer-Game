from django.urls import path,re_path
from . import consumers

websocket_urlpatterns = [
    
    path('ws/livepool/<str:pool_name>/', consumers.LivePoolConsumer.as_asgi()),
     re_path(r'ws/game/(?P<room_code>\w+)/$', consumers.GameRoom.as_asgi()),

     #re_path(r'^ws/livepool/(?P<pool_name>\w+)/$', consumers.LivePoolConsumer.as_asgi()),
   # re_path(r'^ws/tictactoe/(?P<room_id>\w+)/$', consumers.TicTacToeConsumer.as_asgi()),
     # re_path(r"ws/game/tictactoe/(?P<room_id>\\w+)/$", consumers.TicTacToeConsumer.as_asgi()),
]
