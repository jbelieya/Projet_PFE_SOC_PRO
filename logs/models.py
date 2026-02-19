from django.db import models

# Create your models here.
class LogPreuve(models.Model):
    incident = models.ForeignKey('incidents.Incident', on_delete=models.CASCADE) 
    commentaire = models.TextField() 
    piece_jointe = models.FileField(upload_to='preuves/', null=True, blank=True) 
    date_ajout = models.DateTimeField(auto_now_add=True) 





