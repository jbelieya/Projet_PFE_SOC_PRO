from django.db import models
from django.conf import settings


# Create your models here.
class HistoriqueAudit(models.Model):
    ACTION_CHOICES = [
    ('LOGIN', 'Connexion'),
    ('LOGOUT', 'Déconnexion'), 
    ('CREATE', 'Création'),
    ('UPDATE', 'Modification'),
    ('DELETE', 'Suppression'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    description_change = models.TextField()
    date_change = models.DateTimeField(auto_now_add=True)
    id_incident = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-date_change']

    def __str__(self):
        return f"{self.user} - {self.action_type} - {self.date_change}"


def create_audit_log(user, action, description, incident_id=None):
        HistoriqueAudit.objects.create(
        user=user,
        action_type=action,
        description_change=description,
        id_incident=incident_id
     )

