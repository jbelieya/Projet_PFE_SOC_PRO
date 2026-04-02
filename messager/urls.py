from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, consumers

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'chats', views.ChatViewSet, basename='chat')

websocket_urlpatterns = [
    path('ws/notifications/<int:user_id>/', consumers.ChatConsumer.as_asgi()),
]

urlpatterns = [
    path('', include(router.urls)),
    path('conversation/<int:other_user_id>/', views.get_conversation, name='conversation'),
]