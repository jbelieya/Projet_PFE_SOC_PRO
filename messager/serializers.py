from django.conf import settings
from .models import ChatView
from rest_framework import serializers


class ChatViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatView
        fields = ['id', 'sender', 'receiver', 'sent_date', 'textContent']