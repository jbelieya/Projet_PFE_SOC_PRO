from django.conf import settings
from .models import ChatView
from rest_framework import serializers


class ChatViewSerializer(serializers.ModelSerializer):
    # Rja3 sender w receiver ka IDs (mish objects)
    sender   = serializers.PrimaryKeyRelatedField(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model  = ChatView
        fields = ['id', 'sender', 'receiver', 'sent_date', 'textContent']