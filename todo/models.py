from django.db import models
from django.conf import settings # <--- Zid hedhi
import uuid

class AIConsultation(models.Model):
    incident_type = models.CharField(max_length=100)
    description = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Badal el relation houni:
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True
    )

    def __str__(self):
        return f"Conseil pour {self.incident_type}"