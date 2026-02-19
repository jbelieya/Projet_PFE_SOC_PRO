from django.db import models
from django.conf import settings


# Create your models here.

class Incident(models.Model):
    SEVERITE_CHOICES = [('P1', 'P1'), ('P2', 'P2'), ('P3', 'P3'), ('P4', 'P4')] 
    STATUT_CHOICES = [('Nouveau', 'Nouveau'), ('En cours', 'En cours'), ('Résolu', 'Résolu'), ('Fermé', 'Fermé')]

    type_incident = models.CharField(max_length=100) 
    severite = models.CharField(max_length=10, choices=SEVERITE_CHOICES) 
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='Nouveau') 
    date_occurrence = models.DateTimeField()
    date_detection = models.DateTimeField()
    date_cloture = models.DateTimeField(null=True, blank=True) 
    description = models.TextField() 
    
    # Clé étrangère vers User (Analyste_Assigne)
    analyste_assigne = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True) 



