from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
       ('ANALYSTE_N1', 'Analyste Niveau 1'),
        ('ANALYSTE_N2', 'Analyste Niveau 2'),
        ('manager', 'Manager SOC'),
    ]
    role=models.CharField(max_length=20, choices=ROLE_CHOICES, default='ANALYSTE_N1')
    telephone = models.CharField(max_length=15,blank=True,null=True)
    is_approved = models.BooleanField(default=False)  # Admin lezem ya3mel validation
    is_verified = models.BooleanField(default=False)  # Code email/sms
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_online = models.BooleanField(default=False)  # Status en ligne
    last_login_time = models.DateTimeField(blank=True, null=True)  # Dernière connexion
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"