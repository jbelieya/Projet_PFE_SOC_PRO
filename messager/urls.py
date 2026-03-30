from django.urls import path, include, re_path
from rest_framework import routers
from . import views
from . import consumers

router = routers.DefaultRouter()
router.register(r'chats', views.ChatViewSet)
router.register(r'users', views.UserViewSet)

# HEDHI LEZEM TKOU_N LIST [] NDHIFA
urlpatterns = [
    path('', include(router.urls)), # Thabet f-el comma hna
    path('api-token-auth/', views.CustomAuthToken.as_view(), name='api_token_auth'),
    path('create-chat/', views.create_new_chat, name='create_new_chat'),
]

# El WebSockets khallihom f-variable wa7dha bech el ASGI ya9raha
websocket_urlpatterns = [
re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),]