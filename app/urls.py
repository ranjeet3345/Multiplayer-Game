
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('livepool/<str:country>/', views.livepool_list, name='livepool_list'),

    
    path("game/<str:room_id>/", views.GameView, name="tictactoe"),

]
