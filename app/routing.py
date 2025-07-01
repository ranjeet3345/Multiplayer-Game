from django.urls import path,re_path
from . import consumers

websocket_urlpatterns = [
     re_path(r"ws/livepool/(?P<groupkaname>\w+)/$", consumers.MyConsumer.as_asgi()),
]
