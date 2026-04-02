from django.db import models
from django.conf import settings  # Import settings hna
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model 

User = get_user_model()

class ChatView(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, related_name='sent_chats')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, related_name='received_chats')
    sent_date = models.DateTimeField('date published')
    textContent = models.TextField(null=False, blank=False)
    
    def __str__(self):
        return f"Chat {self.id} from {self.sender} to {self.receiver}"
    
    @staticmethod
    def create_chat(message, senderid, receiverid):
        sender_obj = get_object_or_404(User, id=int(senderid))
        receiver_obj = get_object_or_404(User, id=int(receiverid))
        chatnew = ChatView(
            sender=sender_obj, 
            receiver=receiver_obj, 
            textContent=message, 
            sent_date=timezone.now()
        )
        chatnew.save()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)